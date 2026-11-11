"""Builds the supplementary 39-column CSV (REQ12, `document/A/AGRI_CARE_
CSV_Design_Guide_v1.0.pdf`) -- a 7th export added **in parallel** to the 6
Session 05 CSVs (project-owner decision 2026-11-05, "parallel combination",
not a replacement; see `deliverables/session05/10_decision_register_vn.md`
mục 10-11 and `11_supplementary_csv_schema_mapping_vn.md`).

Column behaviour (per the mapping spec's MAP/DERIVED/MISSING_FIELD/
OUTSIDE_DATA classification and the project owner's 2026-11-05 decision
"leave ambiguous columns blank, do not invent aggregation rules"):

- MAP columns (A01-A05, B01-B04) are copied straight from the already
  human-filled Manual Review row / the matching Candidate row.
- OUTSIDE_DATA columns (A06 age_at_anchor, A07 sex, A16 drug_record_date,
  A19 infusion_action_date) are ALWAYS "" -- this data does not exist in
  the profiled source DB (Session 02), not a tool limitation to work
  around.
- DERIVED columns whose aggregation/representative-row-selection rule is
  not yet approved (A09 candidate_anchor_date, A10 anchor_precision, A11-
  A13 diagnosis_*, A14-A15 injection_drug_*, A17 formulation_route_hint,
  A18 infusion_action_name, A20 evidence_ref) are ALWAYS "" -- see
  UNDECIDED-S05-04..10 in the mapping spec. B12 followup_status (vocab
  mapping ambiguous, UNDECIDED-S05-12) is likewise always "".
- A08 hit_pattern IS computed (project-owner decision D1, 2026-11-08, see
  deliverables/session00/11_addendum_csv_v1.1_revision_plan_2026-11-08.md
  §5): "DX"/"RX"/"IV" per CSV Design Guide v1.1 §3, one per axis that
  matched (`in_set_a_q10`/`in_set_b_q20`/`in_set_c_wide_qc1` on the
  candidate row), multiple values joined with "; " (this project's
  existing multi-value separator, see `services/aggregate.py`
  `q40_hint_matched_text` -- the document only specifies "a separator",
  not which character).
- B13 admission_type IS now a pass-through (ADDENDUM 2026-11-08) from the
  Outcome template's new `admission_type` column -- still always a human-
  entered value (DB has no admission-type data at all, `in_out` 100%
  empty, confirmed directly against orca_snapshot.db), and the business
  *scope* of "入院" (all admissions vs. unplanned-only) remains
  UNDECIDED-S05-13; this module only copies whatever text a reviewer typed.
- B06-B11 (admission/transport/death within 30 days) ARE computed, from
  the already human-filled Outcome rows for the same episode_id, using the
  3-value あり/なし/不明 logic in the CSV Design Guide §9: "Y" if a
  matching outcome_type row exists; "不明" if no matching row exists but
  some outcome row for this episode has outcome_tracking_status =
  NOT_CONFIRMABLE; "N" if no matching row exists but some outcome row is
  tracking-confirmed (CONFIRMED_WITHIN_WINDOW / CONFIRMED_OUTSIDE_WINDOW /
  NO_OUTCOME); "" if no outcome data has been imported for this episode at
  all yet. PLANNED_HOSPITALIZATION_EXCLUDED is deliberately excluded from
  the admission_30d match set (R06 -- planned hospitalization does not
  count), consistent with the existing Outcome template semantics.
- B05/B14/B15/B16/B17/C (qc_status, qc_issue) are PASS-THROUGH ONLY from
  the new columns added to the Manual Review / Outcome templates
  (DEC-S05-ADD-01 option a, 2026-11-05) -- this module never computes or
  infers their value, only copies what a human already entered.

This module never fills a clinical/review column (CLAUDE.md mục 3) and
requires the same precondition as `exports.review_template.
build_outcome_template_blank`: rows must come from an already human-filled
Manual Review upload with a real (non-NA) episode_id.
"""
from __future__ import annotations

import pandas as pd

from models.csv_schemas import SUPPLEMENTARY_COLUMNS

_CASE_STATUS_MAP = {"SUBJECT": "対象", "NOT_SUBJECT": "対象外", "PENDING": "保留"}

_ADMISSION_TYPES = {"UNPLANNED_HOSPITALIZATION"}
_TRANSPORT_TYPES = {"EMERGENCY_VISIT"}
_DEATH_TYPES = {"DEATH"}
_TRACKING_CONFIRMED = {"CONFIRMED_WITHIN_WINDOW", "CONFIRMED_OUTSIDE_WINDOW", "NO_OUTCOME"}

# A08 hit_pattern (D1, 2026-11-08): which axis a candidate matched on.
_HIT_PATTERN_AXES = (("in_set_a_q10", "DX"), ("in_set_b_q20", "RX"), ("in_set_c_wide_qc1", "IV"))


def _hit_pattern(candidate: dict) -> str:
    return "; ".join(label for key, label in _HIT_PATTERN_AXES if candidate.get(key) == "Y")


def _first_nonempty(rows: list[dict], key: str) -> str:
    for row in rows:
        val = row.get(key, "")
        if val and str(val).upper() != "NA":
            return val
    return ""


def _event_30d(episode_outcome_rows: list[dict], outcome_types: set[str]) -> tuple[str, str]:
    """Returns (flag, date) using the CSV Design Guide §9 3-value logic."""
    matched = [o for o in episode_outcome_rows if o.get("outcome_type") in outcome_types]
    if matched:
        return "Y", matched[0].get("outcome_date", "")
    if any(o.get("outcome_tracking_status") == "NOT_CONFIRMABLE" for o in episode_outcome_rows):
        return "不明", ""
    if any(o.get("outcome_tracking_status") in _TRACKING_CONFIRMED for o in episode_outcome_rows):
        return "N", ""
    return "", ""


def build_supplementary_export(
    candidate_rows: list[dict],
    review_rows_with_episode: list[dict],
    outcome_rows: list[dict],
) -> pd.DataFrame:
    """One row per episode_id taken from an already-filled-in Manual Review
    file -- same precondition as build_outcome_template_blank. See module
    docstring for exactly which columns are computed vs. always blank."""
    candidates_by_id = {c["candidate_id"]: c for c in candidate_rows}

    rows = []
    for r in review_rows_with_episode:
        episode_id = r.get("episode_id")
        if not episode_id or str(episode_id).upper() == "NA":
            continue

        candidate_id = r.get("candidate_id", "")
        candidate = candidates_by_id.get(candidate_id, {})
        episode_outcome_rows = [o for o in outcome_rows if o.get("episode_id") == episode_id]

        admission_30d, admission_date = _event_30d(episode_outcome_rows, _ADMISSION_TYPES)
        transport_30d, transport_date = _event_30d(episode_outcome_rows, _TRANSPORT_TYPES)
        death_30d, death_date = _event_30d(episode_outcome_rows, _DEATH_TYPES)

        rows.append({
            "extract_batch_id": r.get("source_run_id", ""),
            "candidate_id": candidate_id,
            "facility_id": r.get("clinic_id", ""),
            "patient_local_id": r.get("patient_id", ""),
            "ehr_source": candidate.get("clinic_tool_group", ""),
            # OUTSIDE_DATA -- not in the profiled source DB.
            "age_at_anchor": "", "sex": "",
            "hit_pattern": _hit_pattern(candidate),
            # UNDECIDED-S05-04..10 -- aggregation rule not yet approved.
            "candidate_anchor_date": "", "anchor_precision": "",
            "diagnosis_name": "", "diagnosis_code": "", "diagnosis_record_date": "",
            "injection_drug_name": "", "injection_drug_code": "",
            # OUTSIDE_DATA (nghiêm trọng) -- DB only has perform_month, not a day.
            "drug_record_date": "",
            "formulation_route_hint": "", "infusion_action_name": "",
            # OUTSIDE_DATA (nhóm NAHT; chưa duyệt cho HOMIS).
            "infusion_action_date": "",
            "evidence_ref": "",
            "episode_id": episode_id,
            "case_status": _CASE_STATUS_MAP.get(r.get("review_decision", ""), ""),
            "case_reason": r.get("review_decision_reason", ""),
            "day0_date": r.get("day0_date", ""),
            "day0_evidence": r.get("day0_evidence", ""),
            "admission_30d": admission_30d, "admission_date": admission_date,
            "transport_30d": transport_30d, "transport_date": transport_date,
            "death_30d": death_30d, "death_date": death_date,
            # UNDECIDED-S05-12 -- vocab mapping not yet approved.
            "followup_status": "",
            # ADDENDUM 2026-11-08 -- pass-through only, see module docstring.
            "admission_type": _first_nonempty(episode_outcome_rows, "admission_type"),
            "outcome_evidence_ref": _first_nonempty(episode_outcome_rows, "outcome_evidence_ref"),
            "last_followup_date": _first_nonempty(episode_outcome_rows, "last_followup_date"),
            "followup_unknown_reason": _first_nonempty(episode_outcome_rows, "followup_unknown_reason"),
            "context_review_flags": r.get("context_review_flags", ""),
            "qc_status": r.get("qc_status", ""),
            "qc_issue": r.get("qc_issue", ""),
        })

    df = pd.DataFrame(rows) if rows else pd.DataFrame(columns=list(SUPPLEMENTARY_COLUMNS))
    return df[list(SUPPLEMENTARY_COLUMNS)]
