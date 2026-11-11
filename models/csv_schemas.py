"""Exact column names and order for the 6 Session 05 output CSVs.

These tuples are copied verbatim from the headers of
deliverables/session05/03..08_..._template.csv (cross-checked against
09_data_dictionary_vn.csv). The dashboard/export code must never invent a
different column name or order -- Session 06 AC-S06-06/07 require the
dashboard's exported files to match these exactly.
"""
from __future__ import annotations

CANDIDATE_COLUMNS: tuple[str, ...] = (
    "run_id", "run_date", "db_fetched_at_naht", "db_fetched_at_homis",
    "q_table_version", "dictionary_version", "candidate_id", "clinic_id",
    "clinic_tool_group", "patient_id", "in_set_a_q10", "in_set_b_q20",
    "in_set_c_wide_qc1", "in_set_c_narrow_qc2", "in_q30", "in_q31", "in_q32",
    "combination_cell", "exclusion_granularity", "d3_judgment_code",
    "competing_diagnosis_flag", "flag_zzz_pending_confirmation",
    "needs_form_check", "q40_hint_count", "n_disease_evidence_rows",
    "n_medication_evidence_rows", "n_procedure_evidence_rows",
    "search_period_start", "search_period_end", "lookback_start_date", "notes",
)

DISEASE_EVIDENCE_COLUMNS: tuple[str, ...] = (
    "run_id", "candidate_id", "clinic_id", "patient_id", "source_table",
    "perform_month", "disease_name_original", "disease_name_normalized",
    "disease_code", "flag_zzz_pending_confirmation", "start_date", "in_out",
    "d1_matched_modifier_id", "d1_state", "d1_category", "d1_category_name_jp",
    "matched_q10", "dictionary_version", "fetched_at", "source_record_ref",
)

MEDICATION_EVIDENCE_COLUMNS: tuple[str, ...] = (
    "run_id", "candidate_id", "clinic_id", "patient_id", "source_table",
    "perform_month", "medication_name_original", "medication_name_normalized",
    "medication_code", "medical_class", "medical_class_name",
    "perform_count_raw", "in_out", "matched_q20", "d2_search_term_id",
    "d2_ingredient_id", "d2_confirmed_status", "d2_group", "needs_form_check",
    "matched_q40_hint", "q40_hint_matched_text", "dictionary_version",
    "fetched_at", "source_record_ref",
)

PROCEDURE_EVIDENCE_COLUMNS: tuple[str, ...] = (
    "run_id", "candidate_id", "clinic_id", "patient_id", "source_table",
    "perform_month", "medical_day", "procedure_evidence_type", "medical_class",
    "medical_class_name", "medication_name_original", "medication_name_normalized",
    "point", "in_out", "open_issue_ref", "dictionary_version", "fetched_at",
    "source_record_ref",
)

MANUAL_REVIEW_COLUMNS: tuple[str, ...] = (
    "candidate_id", "clinic_id", "patient_id", "source_run_id", "episode_id",
    "episode_seq", "prior_episode_id", "review_decision", "review_decision_reason",
    "day0_date", "day0_date_source", "end_of_life_care_at_day0",
    "end_of_life_care_change_after_day0", "respiratory_infection_purpose_confirmed",
    "home_administration_confirmed", "episode_boundary_rule_applied",
    "d3_judgment_code_at_review", "dictionary_version_at_review",
    "q_table_version_at_review", "reviewer_id", "review_date", "review_notes",
    # ADDENDUM 2026-11-05 (DEC-S05-ADD-01 option a) -- support columns
    # B05/B17/C of the supplementary 39-column export (REQ12). Always blank
    # in the tool-generated template; only ever filled by a human reviewer.
    "day0_evidence", "context_review_flags", "qc_status", "qc_issue",
)

OUTCOME_COLUMNS: tuple[str, ...] = (
    "episode_id", "candidate_id", "clinic_id", "patient_id", "day0_date",
    "observation_window_definition", "observation_window_end_date",
    "outcome_tracking_status", "outcome_type", "outcome_date",
    "outcome_evidence_source", "outcome_confirmed_by_billing_hint_only",
    "q40_hint_reference", "reviewer_id", "review_date", "notes",
    # ADDENDUM 2026-11-05 (DEC-S05-ADD-01 option a) -- support columns
    # B14/B15/B16 of the supplementary 39-column export (REQ12). Always
    # blank in the tool-generated template; only ever filled by a human.
    "outcome_evidence_ref", "last_followup_date", "followup_unknown_reason",
    # ADDENDUM 2026-11-08 -- B13 admission_type (v1.1 §3: 予定/予定外/不明).
    # DB has no admission-type data at all (`in_out` 100% empty, verified
    # directly against orca_snapshot.db) so this is always a human-entry
    # field; adding the column just gives the reviewer somewhere to type
    # it (CSV Design Guide v1.1 UNDECIDED-S05-13 -- the *scope* of "入院"
    # itself is still open, but the missing input field was the more
    # urgent gap, see deliverables/session00/12_danh_gia_dap_ung_csv_v1.1_
    # 2026-11-08.md §5.2).
    "admission_type",
)

# ADDENDUM 2026-11-05 -- the 39-column supplementary export (REQ12), verbatim
# from deliverables/session05/12_supplementary_csv_template.csv header,
# which itself transcribes document/A/AGRI_CARE_CSV_Design_Guide_v1.0.pdf.
# Most A-columns are left blank by exports/supplementary_export.py pending
# project-owner approval of their aggregation rules (see
# deliverables/session05/11_supplementary_csv_schema_mapping_vn.md
# UNDECIDED-S05-01..17) -- this tuple only fixes the header/column order.
SUPPLEMENTARY_COLUMNS: tuple[str, ...] = (
    "extract_batch_id", "candidate_id", "facility_id", "patient_local_id",
    "ehr_source", "age_at_anchor", "sex", "hit_pattern", "candidate_anchor_date",
    "anchor_precision", "diagnosis_name", "diagnosis_code", "diagnosis_record_date",
    "injection_drug_name", "injection_drug_code", "drug_record_date",
    "formulation_route_hint", "infusion_action_name", "infusion_action_date",
    "evidence_ref", "episode_id", "case_status", "case_reason", "day0_date",
    "day0_evidence", "admission_30d", "admission_date", "transport_30d",
    "transport_date", "death_30d", "death_date", "followup_status",
    "admission_type", "outcome_evidence_ref", "last_followup_date",
    "followup_unknown_reason", "context_review_flags", "qc_status", "qc_issue",
)

# The 5 missing-value tokens, per Session 05 §6 / Session 06 AC-S06-09.
# "" (true blank) is a 6th valid state but is not a token -- it is simply
# omitted here.
NA = "NA"
UNKNOWN = "UNKNOWN"
UNCONFIRMED = "UNCONFIRMED"
NOT_CONFIRMABLE = "NOT_CONFIRMABLE"

# The 7 cells of the A/B/C combination matrix (04_candidate_combination_matrix_vn.md).
COMBINATION_CELLS: tuple[str, ...] = (
    "A_only", "B_only", "C_only", "A_and_B(=Q30)", "A_and_C_not_B",
    "B_and_C_not_A", "A_and_B_and_C",
)
