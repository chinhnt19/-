"""Loader + derived constants for the v1.3.1 candidate-extraction conditions.

`rules/q_conditions.json` holds the v1.3.1 single-path model (V1-DRUG AND
V1-ROUTE, grouped by contiguous billed months -- see its own `_meta`/
`v1_3_1_candidate_conditions`). The v1.0 3-axis model (Q01/Q10/Q20/Q30/Q31/
Q32/Q40, QC1/QC2) it replaces is kept, unmodified, in
`deliverables/session4/02_q_conditions.json` for research-definition
version history -- it is not deleted, just no longer the active pipeline.

This module only loads the JSON and exposes the few constants the matching
engine needs in code form. If the JSON content changes version, these
constants must be re-derived by a human from the new JSON, not silently
kept.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve().parent
Q_CONDITIONS_PATH = _HERE / "q_conditions.json"

# V1-ROUTE: medical_class values that make a 注射用抗菌薬 record candidate-
# eligible, and the A13 route they map to. Values confirmed against real
# data in Session 02 (皮下筋肉内注射=31/静脈注射=32/点滴注射=33); 31 is
# intentionally excluded (D4 P01-P03: 候補にしない). See q_conditions.json
# V1-ROUTE.open_issues for the known P08 (inpatient, class 33) and P11
# (中心静脈注射, not observed under any medical_class yet) caveats.
ELIGIBLE_INJECTION_MEDICAL_CLASSES: dict[str, str] = {"32": "静注", "33": "点滴静注"}
EXCLUDED_INJECTION_MEDICAL_CLASSES: frozenset[str] = frozenset({"31"})

# V1-MONTH-GROUP: only candidates whose first eligible billed month falls in
# this range are output (手順書v1.3.1 §3 対象期間, CSV設計説明書v1.3.1 §6.1).
STUDY_PERIOD_FIRST_MONTH = "2025-09"
STUDY_PERIOD_LAST_MONTH = "2026-08"
# Records are read through one month past the study period end, since a
# candidate's *last* billed month (not just its first) can extend beyond it.
READ_PERIOD_LAST_MONTH = "2026-09"

# A gap of this many consecutive un-billed months breaks a candidate in two
# (V1-MONTH-GROUP: "算定のない月を1か月以上挟んだら、別の候補にする").
MONTH_GAP_BREAKS_CANDIDATE = 1


def load_q_conditions() -> dict[str, Any]:
    with open(Q_CONDITIONS_PATH, encoding="utf-8") as f:
        return json.load(f)
