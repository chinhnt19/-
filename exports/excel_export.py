"""Per-clinic Excel export helpers -- user request 2026-11-16: the download
on the "Xuất dữ liệu" page should be split one file per clinic (facility_id)
instead of one combined file for the whole run, the filename should carry
the clinic's name, and the file format itself should be .xlsx instead of
.csv.

This module only handles splitting/serialization. The DataFrame content and
column order still come from exports/export_csv.py / exports/review_template.py
unchanged -- it does not re-derive or reinterpret any candidate/review data.
"""
from __future__ import annotations

import re
from io import BytesIO

import pandas as pd

_UNSAFE_FILENAME_CHARS = re.compile(r'[\\/:*?"<>|]')


def sanitize_filename_component(text: str) -> str:
    """Strip characters illegal in Windows/macOS/Linux filenames and collapse
    whitespace to "_". Japanese characters (kanji/kana, e.g. clinic_name's
    "アグリホームクリニック ひたち") are left as-is -- valid in filenames on
    every OS this app targets, and already the readable/furigana-like form
    clinic_master stores."""
    cleaned = _UNSAFE_FILENAME_CHARS.sub("", text)
    return re.sub(r"\s+", "_", cleaned).strip("_")


def split_by_facility(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Group an export DataFrame by facility_id, preserving column order
    within each group -- one group per clinic present in the current result
    set. Returns {} for an empty df or one without a facility_id column."""
    if df.empty or "facility_id" not in df.columns:
        return {}
    return {
        str(facility_id): group.reset_index(drop=True)
        for facility_id, group in df.groupby("facility_id", sort=True)
    }


def df_to_excel_bytes(df: pd.DataFrame, sheet_name: str = "Sheet1") -> bytes:
    """Serialize a DataFrame to .xlsx bytes (single sheet), for st.download_button."""
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    return buffer.getvalue()
