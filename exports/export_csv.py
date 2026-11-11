"""Builds the 4 machine-generated CSVs (Candidate + 3 Evidence) as
pandas DataFrames with the exact column names/order of
deliverables/session05/03-06_..._template.csv (models/csv_schemas.py).

These are pure functions over a services.aggregate.PipelineResult -- no
file I/O, no DB access, no UI. Callers (the Streamlit pages) decide where
the resulting DataFrame goes (st.download_button, etc).
"""
from __future__ import annotations

import pandas as pd

from models.csv_schemas import (
    CANDIDATE_COLUMNS, DISEASE_EVIDENCE_COLUMNS, MEDICATION_EVIDENCE_COLUMNS,
    PROCEDURE_EVIDENCE_COLUMNS,
)
from services.aggregate import PipelineResult


def _to_df(rows: list[dict], columns: tuple[str, ...]) -> pd.DataFrame:
    if not rows:
        return pd.DataFrame(columns=list(columns))
    df = pd.DataFrame(rows)
    return df[list(columns)]


def build_candidate_csv(result: PipelineResult, candidate_ids: set[str] | None = None) -> pd.DataFrame:
    rows = result.candidates
    if candidate_ids is not None:
        rows = [r for r in rows if r["candidate_id"] in candidate_ids]
    return _to_df(rows, CANDIDATE_COLUMNS)


def build_disease_evidence_csv(result: PipelineResult, candidate_ids: set[str] | None = None) -> pd.DataFrame:
    rows = result.disease_evidence
    if candidate_ids is not None:
        rows = [r for r in rows if r["candidate_id"] in candidate_ids]
    return _to_df(rows, DISEASE_EVIDENCE_COLUMNS)


def build_medication_evidence_csv(result: PipelineResult, candidate_ids: set[str] | None = None) -> pd.DataFrame:
    rows = result.medication_evidence
    if candidate_ids is not None:
        rows = [r for r in rows if r["candidate_id"] in candidate_ids]
    return _to_df(rows, MEDICATION_EVIDENCE_COLUMNS)


def build_procedure_evidence_csv(result: PipelineResult, candidate_ids: set[str] | None = None) -> pd.DataFrame:
    rows = result.procedure_evidence
    if candidate_ids is not None:
        rows = [r for r in rows if r["candidate_id"] in candidate_ids]
    return _to_df(rows, PROCEDURE_EVIDENCE_COLUMNS)
