"""Shared setup imported at the top of every page: puts the project root on
sys.path (so `database.*` / `services.*` / ... import correctly regardless
of which page Streamlit started from) and holds the cached DB
connection/dictionary singletons.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st  # noqa: E402

from database.db_access import DEFAULT_DB_PATH, connect_readonly, get_clinic_master  # noqa: E402
from rules.clinic_master_overrides import apply_overrides  # noqa: E402
from services.dictionaries import AllDictionaries, load_all  # noqa: E402


@st.cache_resource
def get_connection():
    """A single read-only SQLite connection, reused across reruns and pages.
    CLAUDE.md mục 4: "Use read-only access to the original database." """
    if not DEFAULT_DB_PATH.exists():
        st.error(f"Không tìm thấy database: {DEFAULT_DB_PATH}")
        st.stop()
    try:
        conn = connect_readonly(DEFAULT_DB_PATH)
        conn.execute("SELECT 1")
    except Exception as exc:  # noqa: BLE001 -- surfaced to the user, not swallowed
        st.error(f"Lỗi kết nối database (chỉ đọc): {exc}")
        st.stop()
    return conn


@st.cache_data
def get_clinic_master_cached() -> "pd.DataFrame":  # noqa: F821
    """clinic_master rows from the real DB, plus any `[UNVERIFIED] clinic_id`
    placeholder rows from rules/clinic_master_overrides.py (INT-00-04) so
    filters/search no longer silently drop clinics missing from the source
    clinic_master table. The DB itself is never written to."""
    return apply_overrides(get_clinic_master(get_connection()))


@st.cache_resource
def get_dictionaries() -> AllDictionaries:
    return load_all()


def known_clinic_ids() -> frozenset[str]:
    return frozenset(get_clinic_master_cached()["clinic_id"])
