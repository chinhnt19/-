from models.csv_schemas import (
    CANDIDATE_COLUMNS, DISEASE_EVIDENCE_COLUMNS, MEDICATION_EVIDENCE_COLUMNS, PROCEDURE_EVIDENCE_COLUMNS,
)
from models.run_meta import RunMeta
from services.aggregate import run_pipeline
from services.dictionaries import load_all
from exports.export_csv import (
    build_candidate_csv, build_disease_evidence_csv, build_medication_evidence_csv, build_procedure_evidence_csv,
)

from tests._fixtures import disease_df, medical_df

DICTS = load_all()


def _run_meta():
    return RunMeta(
        run_id="TEST-RUN", run_date="2026-11-04", q_table_version="v1.0", dictionary_version="v1.0",
        db_fetched_at_naht="NA", db_fetched_at_homis="NA", search_period_start="2025-10",
        search_period_end="2026-09", lookback_start_date="2025-07", exclusion_granularity="patient_whole_period",
    )


def test_q30_candidate_full_matrix_cell():
    d_df = disease_df([{"patient_id": "P1", "disease_name": "誤嚥性肺炎"}])
    m_df = medical_df([{"patient_id": "P1", "medication_name": "セフトリアキソンナトリウム注射用1g", "medical_class": "33"}])
    result = run_pipeline(d_df, m_df, None, DICTS, _run_meta(), frozenset({"clinic_test"}))

    assert len(result.candidates) == 1
    cand = result.candidates[0]
    assert cand["candidate_id"] == "clinic_test:P1"
    assert cand["in_set_a_q10"] == "Y"
    assert cand["in_set_b_q20"] == "Y"
    assert cand["in_set_c_wide_qc1"] == "Y"
    assert cand["in_q30"] == "Y"
    assert cand["in_q31"] == "N" and cand["in_q32"] == "N"
    assert cand["combination_cell"] == "A_and_B_and_C"
    assert cand["d3_judgment_code"] == "A"
    assert cand["n_disease_evidence_rows"] == 1
    assert cand["n_medication_evidence_rows"] == 1
    assert cand["n_procedure_evidence_rows"] == 1


def test_q31_antibiotic_without_matching_disease():
    d_df = disease_df([{"patient_id": "P2", "disease_name": "高血圧症"}])  # Z category, not Q10
    m_df = medical_df([{"patient_id": "P2", "medication_name": "セフトリアキソンナトリウム注射用1g", "medical_class": "90"}])
    result = run_pipeline(d_df, m_df, None, DICTS, _run_meta(), frozenset({"clinic_test"}))

    cand = next(c for c in result.candidates if c["patient_id"] == "P2")
    assert cand["in_set_a_q10"] == "N"
    assert cand["in_q31"] == "Y"
    assert cand["combination_cell"] == "B_only"
    assert cand["d3_judgment_code"] == "NA"  # only computed within Q30
    assert cand["q40_hint_count"] == "NA"


def test_q32_disease_without_matching_antibiotic():
    d_df = disease_df([{"patient_id": "P3", "disease_name": "誤嚥性肺炎"}])
    m_df = medical_df([{"patient_id": "P3", "medication_name": "アセトアミノフェン錠", "medical_class": "21"}])
    result = run_pipeline(d_df, m_df, None, DICTS, _run_meta(), frozenset({"clinic_test"}))

    cand = next(c for c in result.candidates if c["patient_id"] == "P3")
    assert cand["in_q32"] == "Y"
    assert cand["combination_cell"] == "A_only"


def test_qc2_reported_as_unconfirmed_never_y():
    # QC2 alone (medical_class 14 does not satisfy QC1) does not make P4 a
    # candidate by itself (QC2 is a side flag, not a 4th matrix axis) --
    # pair it with a QC1-qualifying class 33 row on the same patient so P4
    # qualifies as a C_only candidate and we can check the QC2 flag on it.
    d_df = disease_df([])
    m_df = medical_df([
        {"patient_id": "P4", "medication_name": "在宅患者訪問点滴注射管理指導料", "medical_class": "14"},
        {"patient_id": "P4", "medication_name": "点滴注射", "medical_class": "33"},
    ])
    result = run_pipeline(d_df, m_df, None, DICTS, _run_meta(), frozenset({"clinic_test"}))

    cand = next(c for c in result.candidates if c["patient_id"] == "P4")
    assert cand["in_set_c_narrow_qc2"] == "UNCONFIRMED"
    assert cand["combination_cell"] == "C_only"


def test_qc2_only_patient_is_not_a_candidate():
    d_df = disease_df([])
    m_df = medical_df([{"patient_id": "P7", "medication_name": "在宅患者訪問点滴注射管理指導料", "medical_class": "14"}])
    result = run_pipeline(d_df, m_df, None, DICTS, _run_meta(), frozenset({"clinic_test"}))
    assert all(c["patient_id"] != "P7" for c in result.candidates)


def test_non_candidate_patient_excluded():
    # no Q10, no Q20, no QC1/QC2 match -> not a candidate at all
    d_df = disease_df([{"patient_id": "P5", "disease_name": "高血圧症"}])
    m_df = medical_df([{"patient_id": "P5", "medication_name": "アセトアミノフェン錠", "medical_class": "21"}])
    result = run_pipeline(d_df, m_df, None, DICTS, _run_meta(), frozenset({"clinic_test"}))
    assert all(c["patient_id"] != "P5" for c in result.candidates)


def test_export_csv_column_schemas_exact():
    d_df = disease_df([{"patient_id": "P1", "disease_name": "誤嚥性肺炎"}])
    m_df = medical_df([{"patient_id": "P1", "medication_name": "セフトリアキソンナトリウム注射用1g", "medical_class": "33"}])
    result = run_pipeline(d_df, m_df, None, DICTS, _run_meta(), frozenset({"clinic_test"}))

    assert list(build_candidate_csv(result).columns) == list(CANDIDATE_COLUMNS)
    assert list(build_disease_evidence_csv(result).columns) == list(DISEASE_EVIDENCE_COLUMNS)
    assert list(build_medication_evidence_csv(result).columns) == list(MEDICATION_EVIDENCE_COLUMNS)
    assert list(build_procedure_evidence_csv(result).columns) == list(PROCEDURE_EVIDENCE_COLUMNS)


def test_zzz_flag_propagates_to_candidate():
    d_df = disease_df([{"patient_id": "P6", "disease_name": "誤嚥性肺炎", "disease_code": "ZZZ1234567"}])
    m_df = medical_df([{"patient_id": "P6", "medication_name": "セフトリアキソンナトリウム注射用1g"}])
    result = run_pipeline(d_df, m_df, None, DICTS, _run_meta(), frozenset({"clinic_test"}))
    cand = next(c for c in result.candidates if c["patient_id"] == "P6")
    assert cand["flag_zzz_pending_confirmation"] == "Y"
    ev = next(e for e in result.disease_evidence if e["candidate_id"] == "clinic_test:P6")
    assert ev["flag_zzz_pending_confirmation"] == "Y"


def test_patient_name_never_in_any_output():
    d_df = disease_df([{"patient_id": "P1", "disease_name": "誤嚥性肺炎"}])
    m_df = medical_df([{"patient_id": "P1", "medication_name": "セフトリアキソンナトリウム注射用1g"}])
    result = run_pipeline(d_df, m_df, None, DICTS, _run_meta(), frozenset({"clinic_test"}))
    for rows in (result.candidates, result.disease_evidence, result.medication_evidence, result.procedure_evidence):
        for row in rows:
            assert "patient_name" not in row
