"""Tests for services/build_candidates.py -- the v1.3.1 single-path model
(V1-DRUG AND V1-ROUTE, grouped by contiguous billed months). Replaces
test_aggregate.py (the old Q10/Q20/Q30 7-cell combination matrix)."""
from models.csv_schemas import CANDIDATE_COLUMNS
from models.run_meta import RunMeta
from services.build_candidates import build_candidates
from services.dictionaries import load_all
from exports.export_csv import build_candidate_csv

from tests._fixtures import disease_df, medical_df

DICTS = load_all()


def _run_meta():
    return RunMeta(
        run_id="TEST-RUN", run_date="2026-11-11", q_table_version="v1.3.1", dictionary_version="v1.3.1",
        db_fetched_at_naht="NA", db_fetched_at_homis="NA", search_period_start="2025-09",
        search_period_end="2026-09", lookback_start_date="2025-09-01",
    )


def test_drug_and_eligible_route_makes_a_candidate():
    d_df = disease_df([{"patient_id": "P1", "disease_name": "誤嚥性肺炎"}])
    m_df = medical_df([{"patient_id": "P1", "medication_name": "セフトリアキソンナトリウム注射用1g", "medical_class": "33"}])
    result = build_candidates(d_df, m_df, DICTS, _run_meta(), frozenset({"clinic_test"}))

    assert len(result.candidates) == 1
    cand = result.candidates[0]
    assert cand["candidate_id"] == "clinic_test:P1:2026-05"
    assert cand["route_class"] == "点滴静注"
    assert cand["diagnosis_names"] == "誤嚥性肺炎"
    assert cand["diagnosis_categories"] == "PS:A"


def test_subcutaneous_im_only_is_not_a_candidate():
    # medical_class 31 (皮下筋肉内注射) is explicitly excluded (D4 P01-P03).
    d_df = disease_df([])
    m_df = medical_df([{"patient_id": "P2", "medication_name": "セフトリアキソンナトリウム注射用1g", "medical_class": "31"}])
    result = build_candidates(d_df, m_df, DICTS, _run_meta(), frozenset({"clinic_test"}))
    assert all(c["patient_local_id"] != "P2" for c in result.candidates)


def test_eligible_route_without_antibiotic_drug_is_not_a_candidate():
    # medical_class 33 alone, but the drug name doesn't match D2 at all.
    d_df = disease_df([])
    m_df = medical_df([{"patient_id": "P3", "medication_name": "アセトアミノフェン錠", "medical_class": "33"}])
    result = build_candidates(d_df, m_df, DICTS, _run_meta(), frozenset({"clinic_test"}))
    assert all(c["patient_local_id"] != "P3" for c in result.candidates)


def test_one_month_gap_splits_into_two_candidates():
    d_df = disease_df([])
    m_df = medical_df([
        {"patient_id": "P4", "perform_month": "2025-09", "medication_name": "セフトリアキソンナトリウム注射用1g"},
        {"patient_id": "P4", "perform_month": "2025-10", "medication_name": "セフトリアキソンナトリウム注射用1g"},
        # 2025-11 skipped -- gap of 1 month
        {"patient_id": "P4", "perform_month": "2025-12", "medication_name": "セフトリアキソンナトリウム注射用1g"},
    ])
    result = build_candidates(d_df, m_df, DICTS, _run_meta(), frozenset({"clinic_test"}))
    cands = sorted((c for c in result.candidates if c["patient_local_id"] == "P4"), key=lambda c: c["first_record_month"])
    assert len(cands) == 2
    assert cands[0]["first_record_month"] == "2025-09" and cands[0]["last_record_month"] == "2025-10"
    assert cands[0]["record_months"] == 2
    assert cands[1]["first_record_month"] == "2025-12" and cands[1]["last_record_month"] == "2025-12"


def test_contiguous_months_stay_one_candidate():
    d_df = disease_df([])
    m_df = medical_df([
        {"patient_id": "P5", "perform_month": "2025-09", "medication_name": "セフトリアキソンナトリウム注射用1g"},
        {"patient_id": "P5", "perform_month": "2025-10", "medication_name": "セフトリアキソンナトリウム注射用1g"},
        {"patient_id": "P5", "perform_month": "2025-11", "medication_name": "セフトリアキソンナトリウム注射用1g"},
    ])
    result = build_candidates(d_df, m_df, DICTS, _run_meta(), frozenset({"clinic_test"}))
    cands = [c for c in result.candidates if c["patient_local_id"] == "P5"]
    assert len(cands) == 1
    assert cands[0]["record_months"] == 3


def test_first_month_before_study_period_is_excluded():
    d_df = disease_df([])
    m_df = medical_df([{"patient_id": "P6", "perform_month": "2025-08", "medication_name": "セフトリアキソンナトリウム注射用1g"}])
    result = build_candidates(d_df, m_df, DICTS, _run_meta(), frozenset({"clinic_test"}))
    assert all(c["patient_local_id"] != "P6" for c in result.candidates)


def test_disease_category_z_never_tagged():
    d_df = disease_df([{"patient_id": "P7", "disease_name": "謎の病気"}])  # falls through to Z
    m_df = medical_df([{"patient_id": "P7", "medication_name": "セフトリアキソンナトリウム注射用1g"}])
    result = build_candidates(d_df, m_df, DICTS, _run_meta(), frozenset({"clinic_test"}))
    cand = next(c for c in result.candidates if c["patient_local_id"] == "P7")
    assert cand["diagnosis_names"] == ""


def test_suspected_and_confirmed_same_name_both_kept_distinct():
    d_df = disease_df([
        {"patient_id": "P8", "disease_name": "尿路感染症の疑い"},
        {"patient_id": "P8", "disease_name": "尿路感染症"},
    ])
    m_df = medical_df([{"patient_id": "P8", "medication_name": "セフトリアキソンナトリウム注射用1g"}])
    result = build_candidates(d_df, m_df, DICTS, _run_meta(), frozenset({"clinic_test"}))
    cand = next(c for c in result.candidates if c["patient_local_id"] == "P8")
    cats = cand["diagnosis_categories"].split("|")
    assert "O:S" in cats and "O:A" in cats, "suspected (S) and confirmed (A) must both appear, never merged"


def test_age_and_sex_always_blank_outside_data():
    d_df = disease_df([])
    m_df = medical_df([{"patient_id": "P9", "medication_name": "セフトリアキソンナトリウム注射用1g"}])
    result = build_candidates(d_df, m_df, DICTS, _run_meta(), frozenset({"clinic_test"}))
    cand = next(c for c in result.candidates if c["patient_local_id"] == "P9")
    assert cand["age_at_start"] == "" and cand["sex"] == ""


def test_patient_name_never_in_any_output():
    d_df = disease_df([{"patient_id": "P1", "disease_name": "誤嚥性肺炎"}])
    m_df = medical_df([{"patient_id": "P1", "medication_name": "セフトリアキソンナトリウム注射用1g"}])
    result = build_candidates(d_df, m_df, DICTS, _run_meta(), frozenset({"clinic_test"}))
    for row in result.candidates:
        assert "patient_name" not in row


def test_export_csv_column_schema_exact():
    d_df = disease_df([{"patient_id": "P1", "disease_name": "誤嚥性肺炎"}])
    m_df = medical_df([{"patient_id": "P1", "medication_name": "セフトリアキソンナトリウム注射用1g"}])
    result = build_candidates(d_df, m_df, DICTS, _run_meta(), frozenset({"clinic_test"}))
    assert list(build_candidate_csv(result).columns) == list(CANDIDATE_COLUMNS)
