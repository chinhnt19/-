"""Reproducibility metadata attached to every candidate row of the unified
v1.3.1 CSV (extract_batch_id, CSV設計説明書v1.3.1 §4.1 A01).

`exclusion_granularity` (patient-whole-period vs. month) was a v1.0 concept
tied to the old Q31/Q32 dictionary-leakage audit queries, which no longer
exist -- v1.3.1 candidates are inherently month-grained from the start, so
there is no longer a choice to record here."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, date


@dataclass(frozen=True)
class RunMeta:
    run_id: str
    run_date: str
    q_table_version: str
    dictionary_version: str
    db_fetched_at_naht: str  # "min/max" ISO date string, or "NA" if scope has no NAHT clinic
    db_fetched_at_homis: str
    search_period_start: str
    search_period_end: str
    lookback_start_date: str


def new_run_id(q_table_version: str, dictionary_version: str, now: datetime | None = None) -> str:
    """{YYYYMMDD}-{HHMMSS}-{short_hash} per Session 05 §3.3. The hash covers
    the dictionary+Q versions (not wall-clock) so it stays deterministic for
    a given version pair within the same second."""
    now = now or datetime.now()
    h = hashlib.sha1(f"{dictionary_version}|{q_table_version}".encode("utf-8")).hexdigest()[:6]
    return f"{now:%Y%m%d}-{now:%H%M%S}-{h}"


def today_str(d: date | None = None) -> str:
    return (d or date.today()).isoformat()
