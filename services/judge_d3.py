"""D3 -- judgment matrix lookup (D1 category x D2 group -> A/B/C/X),
APPLY-1..5 (D3_judgment.csv APPLICATION_RULE rows; dictionary_specification.md
§6; 03_candidate_extraction_algorithm_vn.md §6).

Only called for candidates with in_q30=Y (09_data_dictionary_vn.csv:
d3_judgment_code is NA otherwise) -- see module docstring note below on the
two synthetic matrix rows.
"""
from __future__ import annotations

from dataclasses import dataclass

from services.dictionaries import D3Dictionary
from rules.q_conditions import (
    Q10_D1_CATEGORIES as _MAIN8,
    D3_URVIBI_CATEGORIES as _URVIBI,
    D3_ROW_URVIBI,
    D3_ROW_NO_RESPIRATORY,
    D3_ROW_PS_PB_PG,
)

_PRIORITY = {"A": 3, "B": 2, "C": 1, "X": 0}
_DOWNGRADE = {"A": "B", "B": "C", "C": "C", "X": "X"}


@dataclass(frozen=True)
class D3Result:
    judgment_code: str  # A|B|C|X
    competing_diagnosis_flag: bool
    temporal_coincidence_confirmed: bool = False  # APPLY-5: always False, pending chart review


def _row_key_for_category(code: str) -> str:
    return D3_ROW_PS_PB_PG if code in ("PS", "PB", "PG") else code


def judge_patient(d1_hits_as: list[tuple[str, str]], d2_groups: list[str], d3: D3Dictionary) -> D3Result:
    """
    d1_hits_as: (category, state) pairs for this patient's D1 hits already
                restricted to state in {A, S} by the caller (H/X never feed D3).
    d2_groups:  D2 group (G1,G2a,G2b,G3,G4,G5,G6 (7 groups)) for every D2 hit of this patient.
    d3:         loaded D3 dictionary (services.dictionaries.load_d3()).
    """
    competing_flag = any(code == "O" for code, _ in d1_hits_as)

    main8_hits = [(code, state) for code, state in d1_hits_as if code in _MAIN8]
    if main8_hits:
        # APPLY-3 (direct branch): one row per main-8 hit, PS/PB/PG collapsed.
        row_states = [(_row_key_for_category(code), state) for code, state in main8_hits]
    else:
        urvibi_states = [state for code, state in d1_hits_as if code in _URVIBI]
        if urvibi_states:
            # APPLY-3 "UR・VI・BIのみ" synthetic row. APPLY-1's per-category
            # downgrade has no single category here; we extend its intent to
            # the synthetic row: downgrade only if EVERY contributing hit is
            # state S (documented interpretation, not in the source text --
            # see Implementation Traceability Report).
            synth_state = "S" if urvibi_states and all(s == "S" for s in urvibi_states) else "A"
            row_states = [(D3_ROW_URVIBI, synth_state)]
        else:
            # APPLY-3 "呼吸器感染症の病名なし" -- every cell on this row is X
            # regardless of state, per D3_judgment.csv.
            row_states = [(D3_ROW_NO_RESPIRATORY, "A")]

    best_code = "X"
    for row_key, state in row_states:
        for group in d2_groups:
            cell = d3.matrix.get((row_key, group))
            if cell is None:
                continue
            if state == "S":
                cell = _DOWNGRADE[cell]  # APPLY-1
            if _PRIORITY[cell] > _PRIORITY[best_code]:
                best_code = cell  # APPLY-2: highest-priority code across all combinations

    return D3Result(judgment_code=best_code, competing_diagnosis_flag=competing_flag)
