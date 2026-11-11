"""Patient-level aggregation: Set A (Q10) / Set B (Q20) / Set C (QC1/QC2) ->
Q30/Q31/Q32, the 7-cell A/B/C combination matrix, D3 judgment, and the 3
evidence tables. This is the only module that groups records by
`(clinic_id, patient_id)` -- every function above this point works strictly
record-by-record (REQ01/REQ04; session4/01_search_logic_specification_vn.md
§3.3: AND between Q10/Q20 is inherently patient-level because the two
source tables share no record-level key).

DEC-05-01 (Session 05, still DRAFT/not yet approved by the project owner):
the Candidate CSV here is the UNION of all 7 matrix cells, not just Q30 --
see deliverables/session05/10_decision_register_vn.md.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from models.csv_schemas import NA, UNCONFIRMED
from models.run_meta import RunMeta
from rules.clinic_tool_mapping import clinic_group
from services.dictionaries import AllDictionaries
from services.evidence import disease_source_ref, medical_source_ref, medical_points_source_ref
from services.judge_d3 import judge_patient
from services.match_records import ClassifiedDiseaseRow, ClassifiedMedicalRow, classify_disease_rows, classify_medical_rows

PatientKey = tuple[str, str]  # (clinic_id, patient_id)


@dataclass
class PipelineResult:
    candidates: list[dict]
    disease_evidence: list[dict]
    medication_evidence: list[dict]
    procedure_evidence: list[dict]
    run_meta: RunMeta


def _group_by_patient(rows: list) -> dict[PatientKey, list]:
    out: dict[PatientKey, list] = {}
    for r in rows:
        out.setdefault((r.clinic_id, r.patient_id), []).append(r)
    return out


def _combination_cell(a: bool, b: bool, c: bool) -> str:
    if a and b and c:
        return "A_and_B_and_C"
    if a and b:
        return "A_and_B(=Q30)"
    if a and c:
        return "A_and_C_not_B"
    if b and c:
        return "B_and_C_not_A"
    if a:
        return "A_only"
    if b:
        return "B_only"
    if c:
        return "C_only"
    raise ValueError("_combination_cell called for a non-candidate (a=b=c=False)")


def run_pipeline(
    disease_df: pd.DataFrame,
    medical_df: pd.DataFrame,
    medical_points_df: pd.DataFrame | None,
    dicts: AllDictionaries,
    run_meta: RunMeta,
    known_clinic_ids: frozenset[str] | None = None,
) -> PipelineResult:
    disease_rows = classify_disease_rows(disease_df, dicts)
    medical_rows = classify_medical_rows(medical_df, dicts)

    by_patient_disease = _group_by_patient(disease_rows)
    by_patient_medical = _group_by_patient(medical_rows)

    set_a = {k for k, rows in by_patient_disease.items() if any(r.matched_q10 for r in rows)}
    set_b = {k for k, rows in by_patient_medical.items() if any(r.matched_q20 for r in rows)}
    set_c_wide = {k for k, rows in by_patient_medical.items() if any(r.qc1_wide for r in rows)}
    set_c_narrow_match = {k for k, rows in by_patient_medical.items() if any(r.qc2_narrow for r in rows)}

    # QC2 (narrow) is a secondary flag on top of the A/B/C_wide matrix, not a
    # 4th axis of it (session4/04_candidate_combination_matrix_vn.md §2:
    # "QC2 đi kèm như cờ phụ, không làm nổ ma trận thành nhiều hơn 7 ô") -- a
    # patient matching ONLY QC2 (no A, no B, no QC1) is therefore not, by
    # this definition, a candidate at all.
    candidate_keys = set_a | set_b | set_c_wide

    candidates: list[dict] = []
    disease_evidence: list[dict] = []
    medication_evidence: list[dict] = []
    procedure_evidence: list[dict] = []

    for key in sorted(candidate_keys):
        clinic_id, patient_id = key
        d_rows: list[ClassifiedDiseaseRow] = by_patient_disease.get(key, [])
        m_rows: list[ClassifiedMedicalRow] = by_patient_medical.get(key, [])

        a, b, c = key in set_a, key in set_b, key in set_c_wide
        c_narrow = key in set_c_narrow_match
        in_q30, in_q31, in_q32 = (a and b), (b and not a), (a and not b)

        competing_flag = any(r.d1_category == "O" and r.d1_state in ("A", "S") for r in d_rows)
        if in_q30:
            d1_hits_as = [(r.d1_category, r.d1_state) for r in d_rows if r.d1_state in ("A", "S")]
            d2_groups = [h.group for r in m_rows for h in r.d2_hits]
            d3_result = judge_patient(d1_hits_as, d2_groups, dicts.d3)
            d3_code = d3_result.judgment_code
            competing_flag = competing_flag or d3_result.competing_diagnosis_flag
            q40_hint_count = sum(1 for r in m_rows if r.q40_hints)
        else:
            d3_code = NA
            q40_hint_count = NA

        notes = []
        if in_q31:
            notes.append("Q31 — có kháng sinh tiêm nhưng không có bệnh danh hô hấp khớp D1 (rà soát bỏ sót)")
        if in_q32:
            notes.append("Q32 — có bệnh danh hô hấp khớp D1 nhưng không có kháng sinh tiêm khớp D2 (rà soát rò từ điển)")

        candidates.append({
            "run_id": run_meta.run_id, "run_date": run_meta.run_date,
            "db_fetched_at_naht": run_meta.db_fetched_at_naht, "db_fetched_at_homis": run_meta.db_fetched_at_homis,
            "q_table_version": run_meta.q_table_version, "dictionary_version": run_meta.dictionary_version,
            "candidate_id": f"{clinic_id}:{patient_id}", "clinic_id": clinic_id,
            "clinic_tool_group": clinic_group(clinic_id, known_clinic_ids), "patient_id": patient_id,
            "in_set_a_q10": "Y" if a else "N", "in_set_b_q20": "Y" if b else "N",
            "in_set_c_wide_qc1": "Y" if c else "N",
            "in_set_c_narrow_qc2": UNCONFIRMED if c_narrow else "N",
            "in_q30": "Y" if in_q30 else "N", "in_q31": "Y" if in_q31 else "N", "in_q32": "Y" if in_q32 else "N",
            "combination_cell": _combination_cell(a, b, c),
            "exclusion_granularity": run_meta.exclusion_granularity,
            "d3_judgment_code": d3_code,
            "competing_diagnosis_flag": "Y" if competing_flag else "N",
            "flag_zzz_pending_confirmation": "Y" if any(r.flag_zzz_pending_confirmation for r in d_rows) else "N",
            "needs_form_check": "Y" if any(r.needs_form_check for r in m_rows) else "N",
            "q40_hint_count": q40_hint_count,
            "n_disease_evidence_rows": len(d_rows), "n_medication_evidence_rows": len(m_rows),
            "n_procedure_evidence_rows": sum(1 for r in m_rows if r.qc1_wide or r.qc2_narrow),
            "search_period_start": run_meta.search_period_start, "search_period_end": run_meta.search_period_end,
            "lookback_start_date": run_meta.lookback_start_date,
            "notes": " ; ".join(notes),
        })

        for r in d_rows:
            disease_evidence.append({
                "run_id": run_meta.run_id, "candidate_id": f"{clinic_id}:{patient_id}",
                "clinic_id": clinic_id, "patient_id": patient_id, "source_table": "disease_records",
                "perform_month": r.perform_month, "disease_name_original": r.disease_name_original,
                "disease_name_normalized": r.disease_name_normalized, "disease_code": r.disease_code or "",
                "flag_zzz_pending_confirmation": "Y" if r.flag_zzz_pending_confirmation else "N",
                "start_date": r.start_date or "", "in_out": r.in_out or "",
                "d1_matched_modifier_id": r.d1_matched_modifier_id or NA,
                "d1_state": r.d1_state, "d1_category": r.d1_category,
                "d1_category_name_jp": r.d1_category_name_jp,
                "matched_q10": "Y" if r.matched_q10 else "N",
                "dictionary_version": run_meta.dictionary_version, "fetched_at": r.fetched_at or "",
                "source_record_ref": disease_source_ref(clinic_id, patient_id, r.perform_month, r.disease_name_original, r.in_out),
            })

        for r in m_rows:
            first_hit = r.d2_hits[0] if r.d2_hits else None
            medication_evidence.append({
                "run_id": run_meta.run_id, "candidate_id": f"{clinic_id}:{patient_id}",
                "clinic_id": clinic_id, "patient_id": patient_id, "source_table": "medical_records",
                "perform_month": r.perform_month, "medication_name_original": r.medication_name_original,
                "medication_name_normalized": r.medication_name_normalized,
                "medication_code": r.medication_code or "", "medical_class": r.medical_class or "",
                "medical_class_name": r.medical_class_name or "", "perform_count_raw": r.perform_count_raw,
                "in_out": r.in_out or "", "matched_q20": "Y" if r.matched_q20 else "N",
                "d2_search_term_id": first_hit.search_term_id if first_hit else NA,
                "d2_ingredient_id": first_hit.ingredient_id if first_hit else NA,
                "d2_confirmed_status": first_hit.confirmed_status if first_hit else NA,
                "d2_group": first_hit.group if first_hit else NA,
                "needs_form_check": "Y" if r.needs_form_check else "N",
                "matched_q40_hint": "Y" if r.q40_hints else "N",
                "q40_hint_matched_text": "; ".join(r.q40_hints),
                "dictionary_version": run_meta.dictionary_version, "fetched_at": r.fetched_at or "",
                "source_record_ref": medical_source_ref(clinic_id, patient_id, r.perform_month, r.medication_code, r.in_out),
            })
            base_ref = medical_source_ref(clinic_id, patient_id, r.perform_month, r.medication_code, r.in_out)
            if r.qc1_wide:
                procedure_evidence.append({
                    "run_id": run_meta.run_id, "candidate_id": f"{clinic_id}:{patient_id}",
                    "clinic_id": clinic_id, "patient_id": patient_id, "source_table": "medical_records",
                    "perform_month": r.perform_month, "medical_day": NA,
                    "procedure_evidence_type": "QC1_WIDE_INJECTION_CLASS",
                    "medical_class": r.medical_class or "", "medical_class_name": r.medical_class_name or "",
                    "medication_name_original": r.medication_name_original,
                    "medication_name_normalized": r.medication_name_normalized,
                    "point": NA, "in_out": r.in_out or "", "open_issue_ref": "OPEN-04-02",
                    "dictionary_version": run_meta.dictionary_version, "fetched_at": r.fetched_at or "",
                    "source_record_ref": base_ref,
                })
            if r.qc2_narrow:
                procedure_evidence.append({
                    "run_id": run_meta.run_id, "candidate_id": f"{clinic_id}:{patient_id}",
                    "clinic_id": clinic_id, "patient_id": patient_id, "source_table": "medical_records",
                    "perform_month": r.perform_month, "medical_day": NA,
                    "procedure_evidence_type": "QC2_NARROW_C005_2",
                    "medical_class": r.medical_class or "", "medical_class_name": r.medical_class_name or "",
                    "medication_name_original": r.medication_name_original,
                    "medication_name_normalized": r.medication_name_normalized,
                    "point": NA, "in_out": r.in_out or "", "open_issue_ref": "OPEN-04-01",
                    "dictionary_version": run_meta.dictionary_version, "fetched_at": r.fetched_at or "",
                    "source_record_ref": base_ref,
                })

    if medical_points_df is not None and not medical_points_df.empty:
        for r in medical_points_df.itertuples(index=False):
            key = (r.clinic_id, r.patient_id)
            if key not in candidate_keys:
                continue
            procedure_evidence.append({
                "run_id": run_meta.run_id, "candidate_id": f"{r.clinic_id}:{r.patient_id}",
                "clinic_id": r.clinic_id, "patient_id": r.patient_id, "source_table": "medical_points",
                "perform_month": r.perform_month, "medical_day": r.medical_day or "",
                "procedure_evidence_type": "MEDICAL_POINTS_DAY_HINT",
                "medical_class": r.medical_class or "", "medical_class_name": r.medical_class_name or "",
                "medication_name_original": NA, "medication_name_normalized": NA,
                "point": str(r.point) if r.point is not None else NA, "in_out": r.in_out or "", "open_issue_ref": "OPEN-04-02",
                "dictionary_version": run_meta.dictionary_version, "fetched_at": r.fetched_at or "",
                "source_record_ref": medical_points_source_ref(r.clinic_id, r.patient_id, r.perform_month, r.medical_day, r.medical_class),
            })
            # keep the candidate-row procedure count in sync with this extra source
            for cand in candidates:
                if cand["candidate_id"] == f"{r.clinic_id}:{r.patient_id}":
                    cand["n_procedure_evidence_rows"] += 1
                    break

    return PipelineResult(
        candidates=candidates, disease_evidence=disease_evidence,
        medication_evidence=medication_evidence, procedure_evidence=procedure_evidence,
        run_meta=run_meta,
    )
