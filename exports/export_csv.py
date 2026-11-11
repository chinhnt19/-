"""Builds the A-block (17-column) CSV the search tool outputs, as a pure
pandas DataFrame with the exact column order of
models.csv_schemas.CANDIDATE_COLUMNS (CSV設計説明書v1.3.1 §4.1).

Pure function over services.build_candidates.CandidateBuildResult -- no
file I/O, no DB access, no UI. Callers (the Streamlit pages) decide where
the resulting DataFrame goes (st.download_button, etc).
"""
from __future__ import annotations

import pandas as pd

from models.csv_schemas import CANDIDATE_COLUMNS
from services.build_candidates import CandidateBuildResult


def build_candidate_csv(result: CandidateBuildResult, candidate_ids: set[str] | None = None) -> pd.DataFrame:
    rows = result.candidates
    if candidate_ids is not None:
        rows = [r for r in rows if r["candidate_id"] in candidate_ids]
    if not rows:
        return pd.DataFrame(columns=list(CANDIDATE_COLUMNS))
    return pd.DataFrame(rows)[list(CANDIDATE_COLUMNS)]
