"""Read-only import of the human-filled unified review CSV (A + B + C,
41 columns -- CSV設計説明書v1.3.1 §4).

Parses an uploaded file into a DataFrame kept only in `st.session_state`
for this session. Never writes/re-saves the file anywhere -- the file a
reviewer filled in is never overwritten by this tool.

v1.0/v1.1 had two separate uploads (Manual Review + Outcome); v1.3.1
merges them into one file, so there is only one parser now.
"""
from __future__ import annotations

import pandas as pd


def parse_review_csv(uploaded_file) -> pd.DataFrame:
    return pd.read_csv(uploaded_file, dtype=str).fillna("")
