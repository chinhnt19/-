"""Supplement for clinic_master rows missing from the source DB.

Read-only rule (CLAUDE.md mục 4: "Use read-only access to the original
database") -- this module NEVER writes to document/B/orca_snapshot.db. It
only appends extra rows, in the app layer, to the clinic_master DataFrame
that pages/filters already read through app/_bootstrap.py.

Source: INT-00-04 (deliverables/session00/08_unresolved_decisions_register.md
mục D) -- `clinic_cl222`/`clinic_cl223`/`clinic_cl228` have real patient data
in disease_records/medical_records/medical_points but no row in
clinic_master, so they were silently excluded from every clinic
picker/filter and from the actual search pipeline (NAHT/HOMIS
classification uses known_clinic_ids = clinic_master's clinic_id set), with
no warning shown anywhere.

Confirmed by data signature (medical_points present, ~27% class-21 oral-med
rows, fetched_at inside the HOMIS crawl window -- see
document/A/clinic_tool_mapping_v1.0.md mục 3) that these 3 belong to the
HOMIS group. Their real clinic_name is NOT recorded anywhere in this DB or
any file in the repo -- per CLAUDE.md mục 3 ("Never invent missing...
terms"), this module does NOT guess a Japanese branch name. The placeholder
is the literal clinic_id tagged `[UNVERIFIED]`, confirmed with the project
owner 2026-11-08, so research/filters stop silently dropping these 3
facilities while the real name is still pending confirmation from the
source ORCA/HOMIS system and backfill into clinic_master.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

OVERRIDES_PATH = Path(__file__).resolve().parent / "clinic_master_overrides.csv"


def load_overrides() -> pd.DataFrame:
    return pd.read_csv(OVERRIDES_PATH, dtype=str)


def apply_overrides(clinic_master: pd.DataFrame) -> pd.DataFrame:
    """Append override rows for clinic_id values not already present in
    clinic_master. Never replaces an existing row -- if clinic_master is
    ever backfilled with the real name, the real DB row wins automatically
    and this override becomes a no-op for that clinic_id."""
    overrides = load_overrides()
    overrides = overrides[~overrides["clinic_id"].isin(clinic_master["clinic_id"])]
    if overrides.empty:
        return clinic_master
    return pd.concat([clinic_master, overrides], ignore_index=True)
