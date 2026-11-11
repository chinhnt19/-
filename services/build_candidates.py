"""Candidate construction for the v1.3.1 single-path model.

Replaces services/aggregate.py's Q10/Q20/Q30 7-cell combination matrix.
A candidate is one contiguous run of billed months, per
(clinic_id, patient_id), where at least one medical_records row is a
candidate signal (V1-DRUG AND V1-ROUTE -- see
services.match_records.ClassifiedMedicalRow.is_candidate_signal and
rules/q_conditions.json). This module never decides treatment episodes,
Day 0, case_status, or outcomes -- that is the chart reviewer's job
(手順書v1.3.1 §3/§4, CSV設計説明書v1.3.1 §6/§7: "検索ツールでは、次の処理をしない:
case_status・Day 0・転帰の値を自動で決める").

age_at_start (A06) and sex (A07) are left blank -- neither
medical_records, disease_records, medical_points nor clinic_master
carries any demographic field (confirmed against the live schema; the
v1.0-era code reached the same "OUTSIDE_DATA" conclusion for these two
columns).

Disease tagging (A14-A16, CSV設計説明書v1.3.1 §6.2) is applied on a
best-effort basis: the spec's rule is "開始日がA09の末日まで、かつ転帰日が
ない又は転帰日がA08の初日以降", but disease_records has no 転帰日 (end/
outcome date) column at all (confirmed against the live schema and
document/C/session02_db_profiling_report_v1.0.md §5) -- so only the
first half of the rule (start_date on/before the window's end) can
actually be evaluated here; the second half is vacuously true for every
row because the field it refers to does not exist. This is a known DB
limitation, not a silent simplification -- flagged again in
deliverables/session00/15_addendum_v1.3.1_migration_plan_2026-11-11.md.
"""
from __future__ import annotations

import calendar
from dataclasses import dataclass

import pandas as pd

from models.csv_schemas import MULTI_VALUE_SEPARATOR
from models.run_meta import RunMeta
from rules.clinic_tool_mapping import clinic_group
from rules.q_conditions import STUDY_PERIOD_FIRST_MONTH, STUDY_PERIOD_LAST_MONTH
from services.dictionaries import AllDictionaries
from services.evidence import medical_source_ref
from services.match_records import (
    ClassifiedDiseaseRow,
    ClassifiedMedicalRow,
    classify_disease_rows,
    classify_medical_rows,
)

PatientKey = tuple[str, str]  # (clinic_id, patient_id)


@dataclass
class CandidateBuildResult:
    candidates: list[dict]
    run_meta: RunMeta


def _month_tuple(m: str) -> tuple[int, int]:
    y, mo = m.split("-")
    return int(y), int(mo)


def _month_str(t: tuple[int, int]) -> str:
    return f"{t[0]:04d}-{t[1]:02d}"


def _next_month(t: tuple[int, int]) -> tuple[int, int]:
    y, mo = t
    return (y, mo + 1) if mo < 12 else (y + 1, 1)


def _month_last_day(m: str) -> str:
    y, mo = _month_tuple(m)
    last_day = calendar.monthrange(y, mo)[1]
    return f"{y:04d}-{mo:02d}-{last_day:02d}"


def _contiguous_month_runs(months: set[str]) -> list[list[str]]:
    """Split a set of 'YYYY-MM' strings into runs with no un-billed month
    between consecutive entries (V1-MONTH-GROUP: a 1+ month gap starts a
    new candidate)."""
    ordered = sorted({_month_tuple(m) for m in months})
    if not ordered:
        return []
    runs: list[list[tuple[int, int]]] = [[ordered[0]]]
    for t in ordered[1:]:
        if t == _next_month(runs[-1][-1]):
            runs[-1].append(t)
        else:
            runs.append([t])
    return [[_month_str(t) for t in run] for run in runs]


def _dedup_join(values: list[str]) -> str:
    seen: list[str] = []
    for v in values:
        if v and v not in seen:
            seen.append(v)
    return MULTI_VALUE_SEPARATOR.join(seen)


def build_candidates(
    disease_df: pd.DataFrame,
    medical_df: pd.DataFrame,
    dicts: AllDictionaries,
    run_meta: RunMeta,
    known_clinic_ids: frozenset[str] | None = None,
) -> CandidateBuildResult:
    disease_rows = classify_disease_rows(disease_df, dicts)
    medical_rows = classify_medical_rows(medical_df, dicts)

    disease_by_patient: dict[PatientKey, list[ClassifiedDiseaseRow]] = {}
    for r in disease_rows:
        disease_by_patient.setdefault((r.clinic_id, r.patient_id), []).append(r)

    signal_by_patient: dict[PatientKey, list[ClassifiedMedicalRow]] = {}
    for r in medical_rows:
        if r.is_candidate_signal:
            signal_by_patient.setdefault((r.clinic_id, r.patient_id), []).append(r)

    candidates: list[dict] = []
    for (clinic_id, patient_id), rows in sorted(signal_by_patient.items()):
        rows_by_month: dict[str, list[ClassifiedMedicalRow]] = {}
        for r in rows:
            rows_by_month.setdefault(r.perform_month, []).append(r)

        for run_months in _contiguous_month_runs(set(rows_by_month)):
            first_month, last_month = run_months[0], run_months[-1]
            if not (STUDY_PERIOD_FIRST_MONTH <= first_month <= STUDY_PERIOD_LAST_MONTH):
                # 手順書v1.3.1 §3 対象期間: only candidates whose first billed
                # month falls in 2025-09..2026-08 are output.
                continue

            run_rows = [r for m in run_months for r in rows_by_month[m]]
            candidate_id = f"{clinic_id}:{patient_id}:{first_month}"

            # V1-DX-TAG: disease names valid during [A08 start, A09 end],
            # deduplicated by exact original disease name (not by category --
            # A14/A15/A16 are parallel, one entry per name). Category Z
            # ("その他") is never output (D1_disease.csv D1-18 disposition).
            window_end = _month_last_day(last_month)
            d_rows = disease_by_patient.get((clinic_id, patient_id), [])
            eligible = [
                r for r in d_rows
                if r.d1_category != "Z" and (r.start_date or "") <= window_end
            ]
            tagged_by_name: dict[str, ClassifiedDiseaseRow] = {}
            for r in sorted(eligible, key=lambda r: r.start_date or ""):
                tagged_by_name.setdefault(r.disease_name_original, r)

            candidates.append({
                "extract_batch_id": run_meta.run_id,
                "candidate_id": candidate_id,
                "facility_id": clinic_id,
                "patient_local_id": patient_id,
                "ehr_source": clinic_group(clinic_id, known_clinic_ids),
                "age_at_start": "",  # OUTSIDE_DATA -- no demographic field in the DB
                "sex": "",  # OUTSIDE_DATA
                "first_record_month": first_month,
                "last_record_month": last_month,
                "record_months": len(run_months),
                "drug_names": _dedup_join([r.medication_name_original for r in run_rows]),
                "drug_codes": _dedup_join([r.medication_code or "" for r in run_rows]),
                "route_class": _dedup_join([r.route_class_a13 or "" for r in run_rows]),
                "diagnosis_names": MULTI_VALUE_SEPARATOR.join(tagged_by_name.keys()),
                "diagnosis_codes": MULTI_VALUE_SEPARATOR.join(
                    r.disease_code or "" for r in tagged_by_name.values()
                ),
                "diagnosis_categories": MULTI_VALUE_SEPARATOR.join(
                    f"{r.d1_category}:{r.d1_state}" for r in tagged_by_name.values()
                ),
                "evidence_ref": _dedup_join([
                    medical_source_ref(clinic_id, patient_id, r.perform_month, r.medication_code, r.in_out)
                    for r in run_rows
                ]),
            })

    return CandidateBuildResult(candidates=candidates, run_meta=run_meta)
