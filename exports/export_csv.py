"""Builds the A-block (17-column) CSV the search tool outputs, as a pure
pandas DataFrame with the exact column order of
models.csv_schemas.CANDIDATE_COLUMNS (CSV設計説明書v1.3.1 §4.1).

Pure function over services.build_candidates.CandidateBuildResult -- no
file I/O, no DB access, no UI. Callers (the Streamlit pages) decide where
the resulting DataFrame goes (st.download_button, etc).
"""
from __future__ import annotations

import pandas as pd

from models.csv_schemas import UNIFIED_CSV_COLUMNS, CANDIDATE_COLUMNS
from services.build_candidates import CandidateBuildResult
from services.column_glossary import COLUMN_GLOSSARY, dictionary_display_name


def build_candidate_csv(result: CandidateBuildResult, candidate_ids: set[str] | None = None) -> pd.DataFrame:
    rows = result.candidates
    if candidate_ids is not None:
        rows = [r for r in rows if r["candidate_id"] in candidate_ids]
    if not rows:
        return pd.DataFrame(columns=list(CANDIDATE_COLUMNS))
    return pd.DataFrame(rows)[list(CANDIDATE_COLUMNS)]


def build_column_dictionary_csv() -> pd.DataFrame:
    """1 row per column of the 41-column unified CSV (番号/列名/型・値/説明),
    straight from services.column_glossary -- the Japanese wording a reviewer
    opening the exported CSV needs to know what each column means (CSV設計
    説明書v1.3.1 §4). A companion file, not embedded in the data CSV itself,
    since CSV has no per-column comment mechanism.

    列名 here is "{label_ja}_{english_key}" (e.g. "患者ID_patient_id"), via
    services.column_glossary.dictionary_display_name -- per project owner
    request 2026-11-12, so a Japanese reviewer sees the meaning right next
    to the real key. This is DIFFERENT from the actual candidate_*.csv/
    review_*.csv header row, which stays the plain English key alone (手順書
    /CSV設計説明書v1.3.1 §3: "1行目は列名（4章の英字の列名）") -- this hybrid
    format is deliberately scoped to this dictionary file only, never to the
    real data CSVs built by build_candidate_csv()/review_template.py."""
    rows = [
        {"番号": entry["code"], "列名": dictionary_display_name(col), "型・値": entry["type_value"], "説明": entry["description"]}
        for col in UNIFIED_CSV_COLUMNS
        if (entry := COLUMN_GLOSSARY.get(col)) is not None
    ]
    return pd.DataFrame(rows, columns=["番号", "列名", "型・値", "説明"])
