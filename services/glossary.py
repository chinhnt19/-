"""Read-only CSV rows for the "Giải thích thuật ngữ" (glossary) page.

Separate from services/dictionaries.py on purpose: that module only models
the fields the matching/judgment engines consume, and its dataclasses are
depended on by services/match_d1.py, match_d2.py, judge_d3.py and their
tests. This module exposes raw CSV rows verbatim (e.g. a MODIFIER's
main_analysis_disposition_jp, a JUDGMENT_CODE's long-form description) for
DISPLAY ONLY, so the glossary page can show extra documentation columns
without touching the matching dataclasses or their tests.

CLAUDE.md mục 3: every value returned here is copied verbatim from
dictionaries/*.csv -- nothing is translated, summarized or reinterpreted.
"""
from __future__ import annotations

import csv
from pathlib import Path

DICT_DIR = Path(__file__).resolve().parents[1] / "dictionaries"


def read_csv_rows(filename: str) -> list[dict[str, str]]:
    with open(DICT_DIR / filename, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))
