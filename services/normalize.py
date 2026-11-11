"""NFKC normalization (REQ05).

SQLite has no built-in Unicode normalization function, so this happens at
the application layer, applied once to both the DB values and the
dictionary terms (session4/01_search_logic_specification_vn.md §3.2 /
§6.5 step 1). The original, un-normalized value is always preserved
alongside the normalized one wherever it is stored (CLAUDE.md mục 3
"Preserve original database values").
"""
from __future__ import annotations

import unicodedata


def nfkc(s: str | None) -> str | None:
    if s is None:
        return None
    return unicodedata.normalize("NFKC", s)
