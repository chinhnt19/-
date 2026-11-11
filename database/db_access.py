"""Read-only access to document/B/orca_snapshot.db.

CLAUDE.md mục 4: "Use read-only access to the original database." Every
connection here is opened with SQLite's `mode=ro` URI flag AND
`PRAGMA query_only = ON` as a second, independent guard -- a write attempt
fails even if a future edit to this file accidentally drops the first guard.

`patient_name` is intentionally never selected by any function in this
module (REQ08 / CLAUDE.md mục 3 "Do not expose patient names") -- it simply
never enters the Python process.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

DEFAULT_DB_PATH = Path(__file__).resolve().parents[1] / "document" / "B" / "orca_snapshot.db"


def connect_readonly(db_path: Path | str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    uri = f"file:{Path(db_path).resolve()}?mode=ro"
    # check_same_thread=False: the Streamlit app caches this connection once
    # (app/_bootstrap.py::get_connection, @st.cache_resource) and reuses it
    # across reruns/pages, which Streamlit can execute on different worker
    # threads -- Python's sqlite3 otherwise raises "SQLite objects created in
    # a thread can only be used in that same thread" even though nothing
    # here ever runs two queries concurrently (Streamlit serializes reruns
    # per session). Safe here specifically because the connection is
    # read-only (mode=ro) + PRAGMA query_only=ON below, and the system
    # SQLite library's default build is thread-safe ("serialized" threading
    # mode) for exactly this kind of shared-connection, no-concurrent-write
    # use -- this flag only disables Python's own same-thread check, not
    # SQLite's internal locking.
    conn = sqlite3.connect(uri, uri=True, check_same_thread=False)
    conn.execute("PRAGMA query_only = ON;")
    return conn


def get_clinic_master(conn: sqlite3.Connection) -> pd.DataFrame:
    return pd.read_sql_query("SELECT clinic_id, clinic_name FROM clinic_master", conn)


def get_table_row_counts(conn: sqlite3.Connection) -> dict[str, int]:
    counts = {}
    for table in ("disease_records", "medical_records", "medical_points", "clinic_master"):
        counts[table] = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    return counts


def get_distinct_patient_count(conn: sqlite3.Connection) -> int:
    """COUNT(DISTINCT clinic_id, patient_id) across all 3 record tables --
    NEVER COUNT(DISTINCT patient_id) alone (patient_id repeats across up to
    19 clinics, Session 02 §6.3)."""
    sql = """
        SELECT COUNT(*) FROM (
            SELECT DISTINCT clinic_id, patient_id FROM disease_records
            UNION
            SELECT DISTINCT clinic_id, patient_id FROM medical_records
            UNION
            SELECT DISTINCT clinic_id, patient_id FROM medical_points
        )
    """
    return conn.execute(sql).fetchone()[0]


def get_fetched_at_range(conn: sqlite3.Connection, clinic_ids: list[str]) -> tuple[str | None, str | None]:
    if not clinic_ids:
        return None, None
    placeholders = ",".join("?" for _ in clinic_ids)
    sql = f"""
        SELECT MIN(fetched_at), MAX(fetched_at) FROM (
            SELECT fetched_at FROM disease_records WHERE clinic_id IN ({placeholders})
            UNION ALL
            SELECT fetched_at FROM medical_records WHERE clinic_id IN ({placeholders})
        )
    """
    row = conn.execute(sql, clinic_ids * 2).fetchone()
    return row[0], row[1]


def get_patient_counts_by_clinic(conn: sqlite3.Connection) -> pd.DataFrame:
    """Distinct (clinic_id, patient_id) count per clinic, across all 3
    tables -- used for the small-facility warning banner (OPEN-05-01) and
    the Block 1 per-clinic breakdown."""
    sql = """
        SELECT clinic_id, COUNT(DISTINCT patient_id) AS n_patients FROM (
            SELECT clinic_id, patient_id FROM disease_records
            UNION
            SELECT clinic_id, patient_id FROM medical_records
            UNION
            SELECT clinic_id, patient_id FROM medical_points
        )
        GROUP BY clinic_id
    """
    return pd.read_sql_query(sql, conn)


def get_unmapped_clinic_summary(conn: sqlite3.Connection) -> pd.DataFrame:
    """clinic_id values with real rows in disease_records/medical_records/
    medical_points but NO row in clinic_master -- these never appear in any
    UI clinic picker (which always sources its options from clinic_master),
    so they are silently excluded from every search run, with no warning
    shown anywhere. Computed live against the real DB, not hardcoded, so
    this stays correct if clinic_master is ever backfilled (INT-00-04,
    deliverables/session00/08_unresolved_decisions_register.md)."""
    sql = """
        SELECT clinic_id,
               (SELECT COUNT(*) FROM disease_records d WHERE d.clinic_id = u.clinic_id) AS n_disease_rows,
               (SELECT COUNT(*) FROM medical_records m WHERE m.clinic_id = u.clinic_id) AS n_medical_rows,
               (SELECT COUNT(*) FROM medical_points p WHERE p.clinic_id = u.clinic_id) AS n_points_rows
        FROM (
            SELECT DISTINCT clinic_id FROM disease_records
            UNION SELECT DISTINCT clinic_id FROM medical_records
            UNION SELECT DISTINCT clinic_id FROM medical_points
        ) u
        WHERE u.clinic_id NOT IN (SELECT clinic_id FROM clinic_master)
        ORDER BY u.clinic_id
    """
    return pd.read_sql_query(sql, conn)


def get_perform_month_bounds(conn: sqlite3.Connection) -> tuple[str | None, str | None]:
    sql = """
        SELECT MIN(perform_month), MAX(perform_month) FROM (
            SELECT perform_month FROM disease_records
            UNION ALL
            SELECT perform_month FROM medical_records
        )
    """
    row = conn.execute(sql).fetchone()
    return row[0], row[1]


def _clinic_month_filter(clinic_ids: list[str] | None, month_start: str | None, month_end: str | None):
    clauses, params = [], []
    if clinic_ids:
        clauses.append(f"clinic_id IN ({','.join('?' for _ in clinic_ids)})")
        params.extend(clinic_ids)
    if month_start:
        clauses.append("perform_month >= ?")
        params.append(month_start)
    if month_end:
        clauses.append("perform_month <= ?")
        params.append(month_end)
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    return where, params


def load_disease_records(
    conn: sqlite3.Connection,
    clinic_ids: list[str] | None = None,
    month_start: str | None = None,
    month_end: str | None = None,
) -> pd.DataFrame:
    """disease_records, read-only, filtered by clinic scope + perform_month
    range. Pipeline step [1] of 03_candidate_extraction_algorithm_vn.md."""
    where, params = _clinic_month_filter(clinic_ids, month_start, month_end)
    sql = f"""
        SELECT clinic_id, patient_id, perform_month, disease_name, disease_code,
               start_date, in_out, fetched_at
        FROM disease_records
        {where}
    """
    return pd.read_sql_query(sql, conn, params=params)


def load_medical_records(
    conn: sqlite3.Connection,
    clinic_ids: list[str] | None = None,
    month_start: str | None = None,
    month_end: str | None = None,
) -> pd.DataFrame:
    where, params = _clinic_month_filter(clinic_ids, month_start, month_end)
    sql = f"""
        SELECT clinic_id, patient_id, perform_month, medication_code, medication_name,
               medical_class, medical_class_name, perform_count, in_out, fetched_at
        FROM medical_records
        {where}
    """
    return pd.read_sql_query(sql, conn, params=params)


def load_medical_points(
    conn: sqlite3.Connection,
    clinic_ids: list[str] | None = None,
    month_start: str | None = None,
    month_end: str | None = None,
) -> pd.DataFrame:
    """medical_points -- HOMIS-only in practice (Session 02 §5: 0 rows for
    all 11 NAHT clinics). Used only as a supplementary day-level hint, never
    to match D1/D2 (03_candidate_extraction_algorithm_vn.md mục 1)."""
    where, params = _clinic_month_filter(clinic_ids, month_start, month_end)
    sql = f"""
        SELECT clinic_id, patient_id, perform_month, medical_day, medical_class,
               medical_class_name, point, in_out, fetched_at
        FROM medical_points
        {where}
    """
    return pd.read_sql_query(sql, conn, params=params)
