"""Tests for exports/supplementary_export.py -- the 39-column supplementary
CSV (REQ12, ADDENDUM 2026-11-05, parallel to the 6 Session 05 CSVs). Small
synthetic fixtures only, no real/de-identified patient data."""
from models.csv_schemas import SUPPLEMENTARY_COLUMNS
from exports.supplementary_export import build_supplementary_export
from services.dictionaries import load_d5

CANDIDATE = {"candidate_id": "clinic_a:P1", "clinic_id": "clinic_a", "patient_id": "P1", "clinic_tool_group": "NAHT"}

_ALWAYS_BLANK_COLUMNS = [
    c for c in SUPPLEMENTARY_COLUMNS
    if c not in {
        "candidate_id", "facility_id", "patient_local_id", "ehr_source",
        "extract_batch_id", "episode_id", "case_status", "case_reason",
        "day0_date", "day0_evidence", "admission_30d", "admission_date",
        "transport_30d", "transport_date", "death_30d", "death_date",
        "outcome_evidence_ref", "last_followup_date", "followup_unknown_reason",
        "context_review_flags", "qc_status", "qc_issue",
        "hit_pattern", "admission_type",  # ADDENDUM 2026-11-08 -- now computed/pass-through.
    }
]


def _review_row(**overrides):
    row = {
        "candidate_id": "clinic_a:P1", "clinic_id": "clinic_a", "patient_id": "P1",
        "source_run_id": "RUN1", "episode_id": "clinic_a:P1-EP01",
        "review_decision": "SUBJECT", "review_decision_reason": "", "day0_date": "2026-05-03",
        "day0_evidence": "", "context_review_flags": "", "qc_status": "", "qc_issue": "",
    }
    row.update(overrides)
    return row


def test_header_matches_supplementary_columns_exactly():
    df = build_supplementary_export([CANDIDATE], [_review_row()], [])
    assert list(df.columns) == list(SUPPLEMENTARY_COLUMNS)
    assert len(SUPPLEMENTARY_COLUMNS) == 39


def test_undecided_and_outside_data_columns_always_blank():
    outcome_rows = [{"episode_id": "clinic_a:P1-EP01", "outcome_type": "UNPLANNED_HOSPITALIZATION",
                      "outcome_date": "2026-05-20", "outcome_tracking_status": "CONFIRMED_WITHIN_WINDOW"}]
    df = build_supplementary_export([CANDIDATE], [_review_row()], outcome_rows)
    for col in _ALWAYS_BLANK_COLUMNS:
        assert (df[col] == "").all(), f"{col} should always be blank (UNDECIDED/OUTSIDE_DATA)"


def test_case_status_vocab_mapping():
    rows = [
        _review_row(episode_id="clinic_a:P1-EP01", review_decision="SUBJECT"),
        _review_row(episode_id="clinic_a:P1-EP02", review_decision="NOT_SUBJECT"),
        _review_row(episode_id="clinic_a:P1-EP03", review_decision="PENDING"),
        _review_row(episode_id="clinic_a:P1-EP04", review_decision="SOMETHING_UNKNOWN"),
    ]
    df = build_supplementary_export([CANDIDATE], rows, [])
    assert df["case_status"].tolist() == ["対象", "対象外", "保留", ""]


def test_admission_transport_death_30d_three_value_logic():
    # Scenario 1: matching outcome_type -> Y + date.
    outcome_y = [{"episode_id": "EP-Y", "outcome_type": "UNPLANNED_HOSPITALIZATION",
                  "outcome_date": "2026-05-20", "outcome_tracking_status": "CONFIRMED_WITHIN_WINDOW"}]
    # Scenario 2: no matching outcome_type, tracking confirmed -> N.
    outcome_n = [{"episode_id": "EP-N", "outcome_type": "NA",
                  "outcome_date": "NA", "outcome_tracking_status": "NO_OUTCOME"}]
    # Scenario 3: tracking NOT_CONFIRMABLE -> 不明.
    outcome_unk = [{"episode_id": "EP-UNK", "outcome_type": "NA",
                    "outcome_date": "NA", "outcome_tracking_status": "NOT_CONFIRMABLE"}]
    reviews = [
        _review_row(episode_id="EP-Y"), _review_row(episode_id="EP-N"), _review_row(episode_id="EP-UNK"),
    ]
    df = build_supplementary_export([CANDIDATE], reviews, outcome_y + outcome_n + outcome_unk)
    by_ep = df.set_index("episode_id")
    assert by_ep.loc["EP-Y", "admission_30d"] == "Y"
    assert by_ep.loc["EP-Y", "admission_date"] == "2026-05-20"
    assert by_ep.loc["EP-N", "admission_30d"] == "N"
    assert by_ep.loc["EP-UNK", "admission_30d"] == "不明"


def test_planned_hospitalization_excluded_not_counted_as_admission():
    outcome_rows = [{"episode_id": "EP-PLANNED", "outcome_type": "PLANNED_HOSPITALIZATION_EXCLUDED",
                      "outcome_date": "2026-05-20", "outcome_tracking_status": "CONFIRMED_WITHIN_WINDOW"}]
    df = build_supplementary_export([CANDIDATE], [_review_row(episode_id="EP-PLANNED")], outcome_rows)
    row = df[df["episode_id"] == "EP-PLANNED"].iloc[0]
    assert row["admission_30d"] == "N"
    assert row["admission_date"] == ""


def test_no_patient_name_column_anywhere():
    df = build_supplementary_export([CANDIDATE], [_review_row()], [])
    assert "patient_name" not in df.columns
    assert all("patient_name" not in str(v) for v in df.to_dict("records")[0].values())


def test_rows_without_valid_episode_id_are_excluded():
    rows = [_review_row(episode_id="NA"), _review_row(episode_id="")]
    df = build_supplementary_export([CANDIDATE], rows, [])
    assert len(df) == 0
    assert list(df.columns) == list(SUPPLEMENTARY_COLUMNS)


def test_hit_pattern_maps_axes_to_dx_rx_iv_and_joins_multiple():
    cand_dx_only = {**CANDIDATE, "candidate_id": "clinic_a:P1", "in_set_a_q10": "Y", "in_set_b_q20": "N", "in_set_c_wide_qc1": "N"}
    cand_all = {**CANDIDATE, "candidate_id": "clinic_a:P2", "patient_id": "P2",
                "in_set_a_q10": "Y", "in_set_b_q20": "Y", "in_set_c_wide_qc1": "Y"}
    cand_none = {**CANDIDATE, "candidate_id": "clinic_a:P3", "patient_id": "P3",
                 "in_set_a_q10": "N", "in_set_b_q20": "N", "in_set_c_wide_qc1": "N"}
    rows = [
        _review_row(candidate_id="clinic_a:P1", episode_id="EP1"),
        _review_row(candidate_id="clinic_a:P2", patient_id="P2", episode_id="EP2"),
        _review_row(candidate_id="clinic_a:P3", patient_id="P3", episode_id="EP3"),
    ]
    df = build_supplementary_export([cand_dx_only, cand_all, cand_none], rows, [])
    by_ep = df.set_index("episode_id")
    assert by_ep.loc["EP1", "hit_pattern"] == "DX"
    assert by_ep.loc["EP2", "hit_pattern"] == "DX; RX; IV"
    assert by_ep.loc["EP3", "hit_pattern"] == ""


def test_admission_type_passes_through_from_outcome_row():
    outcome_rows = [{"episode_id": "EP-ADM", "outcome_type": "UNPLANNED_HOSPITALIZATION",
                      "outcome_date": "2026-05-20", "outcome_tracking_status": "CONFIRMED_WITHIN_WINDOW",
                      "admission_type": "予定外"}]
    df = build_supplementary_export([CANDIDATE], [_review_row(episode_id="EP-ADM")], outcome_rows)
    row = df[df["episode_id"] == "EP-ADM"].iloc[0]
    assert row["admission_type"] == "予定外"


def test_load_d5_returns_12_codes():
    d5 = load_d5()
    assert len(d5.flags) == 12
    codes = {f.code for f in d5.flags}
    assert codes == {
        "PRIOR_INPATIENT_ABX", "TRANSFERRED_DOCUMENT", "SOURCE_CONFLICT", "BASELINE_CARE_PLAN",
        "POST_DAY0_CARE_PLAN", "LINKAGE_UNVERIFIED", "EPISODE_BOUNDARY_REVIEW", "OVERLAPPING_WINDOWS",
        "SAME_DAY_ORDER_UNCLEAR", "DUPLICATE_EVENT_SOURCE", "DATE_PRECISION_LIMITED", "REGIMEN_OR_ROUTE_CHANGE",
    }
