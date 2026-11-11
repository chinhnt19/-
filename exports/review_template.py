"""Builds the 2 human-authored templates (Manual Review / Outcome) -- blank
except for identity columns. Per CLAUDE.md mục 3 / Session 05 §9, no module
anywhere in this app may fill in a clinical column (review_decision,
day0_date, episode_id, outcome_type, ...) -- only a human reviewer does,
outside this tool. There is deliberately no "write"/"update" function here
that re-saves an already-filled template; this module only ever produces a
fresh blank one.
"""
from __future__ import annotations

import pandas as pd

from models.csv_schemas import MANUAL_REVIEW_COLUMNS, OUTCOME_COLUMNS


def build_review_template_blank(
    candidate_rows: list[dict],
    source_run_id: str,
    q_table_version: str,
    dictionary_version: str,
) -> pd.DataFrame:
    """One row per candidate, identity + (for reference only, per Session 05
    §5/Block 7) the D3 code and dictionary/Q versions AT THE TIME OF EXPORT.
    Every clinical column is left truly blank -- this is a file for a human
    to fill in, not a machine-generated one waiting to be completed."""
    rows = []
    for c in candidate_rows:
        rows.append({
            "candidate_id": c["candidate_id"], "clinic_id": c["clinic_id"], "patient_id": c["patient_id"],
            "source_run_id": source_run_id, "episode_id": "", "episode_seq": "", "prior_episode_id": "",
            "review_decision": "", "review_decision_reason": "", "day0_date": "", "day0_date_source": "",
            "end_of_life_care_at_day0": "", "end_of_life_care_change_after_day0": "",
            "respiratory_infection_purpose_confirmed": "", "home_administration_confirmed": "",
            "episode_boundary_rule_applied": "", "d3_judgment_code_at_review": c.get("d3_judgment_code", ""),
            "dictionary_version_at_review": dictionary_version, "q_table_version_at_review": q_table_version,
            "reviewer_id": "", "review_date": "", "review_notes": "",
            # ADDENDUM 2026-11-05 (DEC-S05-ADD-01 option a) -- blank, human-only.
            "day0_evidence": "", "context_review_flags": "", "qc_status": "", "qc_issue": "",
        })
    df = pd.DataFrame(rows) if rows else pd.DataFrame(columns=list(MANUAL_REVIEW_COLUMNS))
    return df[list(MANUAL_REVIEW_COLUMNS)]


def build_outcome_template_blank(review_rows_with_episode: list[dict]) -> pd.DataFrame:
    """One row per episode_id taken from an already-filled-in Manual Review
    file (uploaded read-only via the import control) -- requires episode_id
    to exist, i.e. review_decision == SUBJECT. Clinical outcome columns are
    left blank; q40_hint_reference is left for the reviewer to fill (any
    automatic suggestion would blur the "hint, not confirmation" boundary)."""
    rows = []
    for r in review_rows_with_episode:
        episode_id = r.get("episode_id")
        if not episode_id or str(episode_id).upper() == "NA":
            continue
        rows.append({
            "episode_id": episode_id, "candidate_id": r.get("candidate_id", ""),
            "clinic_id": r.get("clinic_id", ""), "patient_id": r.get("patient_id", ""),
            "day0_date": r.get("day0_date", ""), "observation_window_definition": "",
            "observation_window_end_date": "", "outcome_tracking_status": "", "outcome_type": "",
            "outcome_date": "", "outcome_evidence_source": "",
            "outcome_confirmed_by_billing_hint_only": "N", "q40_hint_reference": "",
            "reviewer_id": "", "review_date": "", "notes": "",
            # ADDENDUM 2026-11-05 (DEC-S05-ADD-01 option a) -- blank, human-only.
            "outcome_evidence_ref": "", "last_followup_date": "", "followup_unknown_reason": "",
            # ADDENDUM 2026-11-08 -- B13 admission_type. DB has no admission-
            # type data (`in_out` always empty); reviewer types one of the
            # v1.1 §3 example values (予定/予定外/不明) by hand. No
            # validation against a fixed list yet -- scope of "入院" itself
            # is still UNDECIDED-S05-13.
            "admission_type": "",
        })
    df = pd.DataFrame(rows) if rows else pd.DataFrame(columns=list(OUTCOME_COLUMNS))
    return df[list(OUTCOME_COLUMNS)]
