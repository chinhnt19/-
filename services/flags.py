"""Small record-level flags that must never be silently reclassified.

Session 02 nghi vấn #3 (open, not resolved by any session): disease_code
values starting with "ZZZ" have no confirmed official meaning yet. They are
flagged, never auto-classified as Outside Dictionary or into any D1
category based on the code (D1 matching only ever looks at disease_name).
"""
from __future__ import annotations


def flag_zzz_pending_confirmation(disease_code: str | None) -> bool:
    return bool(disease_code) and disease_code.startswith("ZZZ")
