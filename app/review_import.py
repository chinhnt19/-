"""Read-only import of human-filled Manual Review / Outcome CSVs.

Parses an uploaded file into a DataFrame kept only in `st.session_state` for
this session. Never writes/re-saves the file anywhere -- Session 05 mục 2:
"File 5-6 do con người tạo, KHÔNG BAO GIỜ bị thuật toán trích xuất ghi đè."
"""
from __future__ import annotations

import pandas as pd


def parse_review_csv(uploaded_file) -> pd.DataFrame:
    return pd.read_csv(uploaded_file, dtype=str).fillna("")


def parse_outcome_csv(uploaded_file) -> pd.DataFrame:
    return pd.read_csv(uploaded_file, dtype=str).fillna("")
