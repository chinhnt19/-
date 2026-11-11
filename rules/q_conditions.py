"""Loader + derived constants for the official Q search conditions.

`rules/q_conditions.json` is a verbatim copy of
deliverables/session4/02_q_conditions.json (Master Document v1.0 Table 7-1/
7-2, plus the two provisional Session 04 proposals QC1/QC2). It is NOT
edited here -- this module only loads it and exposes the few constants the
matching engine needs in code form. If the JSON content changes version,
this file's constants must be re-derived by a human from the new JSON, not
silently kept.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve().parent
Q_CONDITIONS_PATH = _HERE / "q_conditions.json"

# D1 categories that count toward Q10 / Set A ("A" in the A/B/C matrix).
# Source: 02_q_conditions.json, Q10.post_processing_vn -- "CHỈ giữ lại các
# bản ghi rơi vào category PS, PB, PG, PA, PL, PV, LB, Q (và chỉ ở trạng
# thái A hoặc S)".
Q10_D1_CATEGORIES: frozenset[str] = frozenset({"PS", "PB", "PG", "PA", "PL", "PV", "LB", "Q"})
Q10_D1_STATES: frozenset[str] = frozenset({"A", "S"})

# D1 categories that, on their own (no Q10_D1_CATEGORIES hit), route a D3
# lookup to the synthetic matrix row "UR・VI・BIのみ" (APPLY-3).
D3_URVIBI_CATEGORIES: frozenset[str] = frozenset({"UR", "VI", "BI"})
D3_ROW_URVIBI = "UR・VI・BIのみ"
D3_ROW_NO_RESPIRATORY = "呼吸器感染症の病名なし"
D3_ROW_PS_PB_PG = "PS・PB・PG"

# QC1 (wide, provisional) -- medical_class values confirmed against real data
# in Session 02 (皮下筋肉内注射/静脈内注射/点滴注射). OPEN-04-02: cannot be
# split further into D4-1's P01-P11 until the DB column mapping is confirmed.
QC1_INJECTION_MEDICAL_CLASSES: frozenset[str] = frozenset({"31", "32", "33"})

# QC2 (narrow, provisional) -- candidate billing-item name string. OPEN-04-01:
# the exact string actually used by ORCA in medication_name is NOT verified
# against real data yet, so any QC2 match must be reported as the
# "UNCONFIRMED" token, never "Y" (see 09_data_dictionary_vn.csv row for
# in_set_c_narrow_qc2).
QC2_C005_2_NAME_CANDIDATE = "在宅患者訪問点滴注射管理指導料"

# Q40 outcome hints (D4-3, P20-P24). P25 ("gap in records") is a separate
# absence-of-record rule, not a substring match -- implemented separately.
Q40_OUTCOME_HINT_TERMS: tuple[str, ...] = (
    "往診料",
    "診療情報提供料",
    "在宅ターミナルケア加算",
    "看取り加算",
    "死亡診断加算",
)

EXCLUSION_GRANULARITY_PATIENT = "patient_whole_period"
EXCLUSION_GRANULARITY_MONTH = "month"


def load_q_conditions() -> dict[str, Any]:
    with open(Q_CONDITIONS_PATH, encoding="utf-8") as f:
        return json.load(f)
