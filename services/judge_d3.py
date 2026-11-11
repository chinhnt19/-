"""D3 -- judgment matrix lookup (D1 category x D2 group -> A/B/C/X),
APPLY-1..5 (D3_judgment.csv APPLICATION_RULE rows; dictionary_specification.md
§6; 03_candidate_extraction_algorithm_vn.md §6).

v1.3.1 status: the matrix/groups/application-rule content is unchanged
from v1.0 (source confirms this), but its MEANING changed from "is this
candidate in the main analysis" to "what order should the reviewer look
at this candidate in" (検索ツール辞書v1.3.1.xlsx D3_判定コード). Candidate
selection no longer depends on this module at all -- v1.3.1 candidates
come purely from services/build_candidates.py (V1-DRUG AND V1-ROUTE).
This module is kept as an OPTIONAL reviewer-facing priority hint; it is
not called from build_candidates.py or any export. Whether the dashboard
should surface it is an open item (deliverables/session00/15_addendum_
v1.3.1_migration_plan_2026-11-11.md §6) -- wire it up only after that is
confirmed, don't let the fact that this function exists imply the
decision was already made.
"""
from __future__ import annotations

from dataclasses import dataclass

from services.dictionaries import D3Dictionary

# D1 categories whose disease name alone is enough to put a patient on the
# "PS・PB・PG"-family rows of the D3 matrix, vs. the two synthetic rows
# below for weaker/no respiratory-disease-name evidence. This grouping is
# purely about which D3 matrix row to look up -- it has no bearing on
# whether a record is a v1.3.1 candidate (that's rules.q_conditions'
# V1-DRUG/V1-ROUTE, an unrelated axis).
_MAIN8 = frozenset({"PS", "PB", "PG", "PA", "PL", "PV", "LB", "Q"})
_URVIBI = frozenset({"UR", "VI", "BI"})
D3_ROW_URVIBI = "UR・VI・BIのみ"
D3_ROW_NO_RESPIRATORY = "呼吸器感染症の病名なし"
D3_ROW_PS_PB_PG = "PS・PB・PG"

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
