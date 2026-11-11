"""Integration smoke test against the REAL orca_snapshot.db (read-only),
restricted to the smallest clinic so it stays fast. Skipped automatically
if the DB file isn't present (e.g. a CI checkout without the data file)."""
import time

import pytest

from database.db_access import (
    DEFAULT_DB_PATH, connect_readonly, get_unmapped_clinic_summary, load_disease_records, load_medical_records,
)
from models.run_meta import RunMeta, new_run_id, today_str
from services.build_candidates import build_candidates
from services.dictionaries import load_all

pytestmark = pytest.mark.skipif(not DEFAULT_DB_PATH.exists(), reason="orca_snapshot.db not present")


def test_smoke_smallest_clinic():
    conn = connect_readonly(DEFAULT_DB_PATH)
    dicts = load_all()
    clinic_ids = ["clinic_sanjou"]  # smallest NAHT clinic, 16 patients total (Session 02)

    t0 = time.time()
    disease_df = load_disease_records(conn, clinic_ids)
    medical_df = load_medical_records(conn, clinic_ids)
    run_meta = RunMeta(
        run_id=new_run_id("v1.3.1", dicts.d1.version), run_date=today_str(),
        q_table_version="v1.3.1", dictionary_version=dicts.d1.version,
        db_fetched_at_naht="NA", db_fetched_at_homis="NA",
        search_period_start="", search_period_end="", lookback_start_date="",
    )
    result = build_candidates(disease_df, medical_df, dicts, run_meta, frozenset(clinic_ids))
    elapsed = time.time() - t0

    assert len(disease_df) > 0
    assert len(medical_df) > 0
    # Every candidate's evidence_ref must be non-empty (traceable back to a real row).
    assert all(c["evidence_ref"] for c in result.candidates)
    print(f"\nclinic_sanjou: {len(disease_df)} disease rows, {len(medical_df)} medical rows, "
          f"{len(result.candidates)} candidates, {elapsed:.2f}s")


def test_unmapped_clinic_summary_columns():
    """INT-00-04: clinic_ids with real data but no clinic_master row stay
    invisible to the UI -- just a shape/column smoke test here, the live
    count is surfaced to the user on the "Giải thích thuật ngữ" page."""
    conn = connect_readonly(DEFAULT_DB_PATH)
    df = get_unmapped_clinic_summary(conn)
    assert list(df.columns) == ["clinic_id", "n_disease_rows", "n_medical_rows", "n_points_rows"]
