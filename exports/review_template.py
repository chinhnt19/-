"""Builds the single unified review CSV (A + blank B + blank C, 41
columns) handed to the chart reviewer -- CSV設計説明書v1.3.1 §4, §6.4.

v1.0/v1.1 had two separate human-authored templates (Manual Review +
Outcome); v1.3.1 merges B (reviewer-filled) and C (QC) into the same file
as A (tool-filled), so there is only one template to build now.

Per CLAUDE.md mục 3 / CSV設計説明書v1.3.1 §7 ("検索ツールでは、次の処理を
しない: case_status・Day 0・転帰の値を自動で決める"), no module anywhere in
this app may fill in a B or C column -- only a human does, outside this
tool. There is deliberately no "write"/"update" function here that
re-saves an already-filled file; this module only ever produces a fresh
blank-B/C copy of the tool's own A-block output.

Episode splitting (CSV設計説明書 §6.4: a candidate whose billed months
contain >=2 treatments gets its row copied, with B01 getting a
"candidate_id-1", "candidate_id-2", ... suffix) is explicitly the
reviewer's manual action on THIS file, not something the tool does --
"検索ツールが最初に出力した行は削除しない。行のコピーは、レビュー用のCSVで
行う。" So this module emits exactly one row per candidate; a reviewer
who needs more than one treatment per candidate copies the row by hand
in their spreadsheet tool before filling B01-B22.
"""
from __future__ import annotations

import pandas as pd

from models.csv_schemas import CANDIDATE_COLUMNS, MANUAL_REVIEW_COLUMNS, QC_COLUMNS, UNIFIED_CSV_COLUMNS


def build_review_csv_blank(candidate_rows: list[dict]) -> pd.DataFrame:
    """One row per candidate: the 17 A columns as produced by the search
    tool, plus the 22 B and 2 C columns all blank for the reviewer/QC
    person to fill in."""
    rows = []
    for c in candidate_rows:
        row = {col: c.get(col, "") for col in CANDIDATE_COLUMNS}
        row.update({col: "" for col in MANUAL_REVIEW_COLUMNS})
        row.update({col: "" for col in QC_COLUMNS})
        rows.append(row)
    df = pd.DataFrame(rows) if rows else pd.DataFrame(columns=list(UNIFIED_CSV_COLUMNS))
    return df[list(UNIFIED_CSV_COLUMNS)]
