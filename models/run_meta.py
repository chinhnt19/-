"""Reproducibility metadata attached to every row of the 4 machine-generated
CSVs (REQ09, Session 05 §3.3/§3.6)."""
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
    exclusion_granularity: str  # EXCLUSION_GRANULARITY_PATIENT | EXCLUSION_GRANULARITY_MONTH


def new_run_id(q_table_version: str, dictionary_version: str, now: datetime | None = None) -> str:
    """{YYYYMMDD}-{HHMMSS}-{short_hash} per Session 05 §3.3. The hash covers
    the dictionary+Q versions (not wall-clock) so it stays deterministic for
    a given version pair within the same second."""
    now = now or datetime.now()
    h = hashlib.sha1(f"{dictionary_version}|{q_table_version}".encode("utf-8")).hexdigest()[:6]
    return f"{now:%Y%m%d}-{now:%H%M%S}-{h}"


def today_str(d: date | None = None) -> str:
    return (d or date.today()).isoformat()
