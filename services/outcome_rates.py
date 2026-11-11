"""Outcome-level aggregation per CSV Design Guide v1.1 §5/§9 -- the
"研究目的の最終集計" layer that, as of the 2026-11-08 session00 assessment
(deliverables/session00/12_danh_gia_dap_ung_csv_v1.1_2026-11-08.md §5.4),
had zero code anywhere, including the dashboard.

Operates only on supplementary-export-shaped episode rows (one dict per
episode_id, the shape produced by `exports.supplementary_export.
build_supplementary_export`) -- never on raw DB rows, and never computes
case_status/day0_date/outcome_type itself (CLAUDE.md muc 3): those are
always a human reviewer's values, taken as given, not re-derived here.

Deliberately NOT modelled yet (needs more than this module can decide):
the §6 "reject-loop" refinement -- "3 転帰 all 'なし' but follow-up
confirmation insufficient" should go back to primary review and only
become 確認不能(U) if that doesn't resolve it (per the v1.1 text itself,
not an invented rule). That needs a Session04-approved spec plus the
B12/B15/B16 vocab mapping (UNDECIDED-S05-12), neither of which exists yet
(deliverables/session00/11_addendum_csv_v1.1_revision_plan_2026-11-08.md
§6, §10 last bullet). Until then, an episode where all 3 outcomes are "N"
is always counted here as 複合「なし」.
"""
from __future__ import annotations

import re

# The 4 "集計保留フラグ" codes (v1.1 §5/§9, verbatim): episodes carrying
# one of these in B17 are excluded from the official denominator T and
# reported separately, pending research-lead approval of the matching
# judgment rule. This list is itself "暫定" per the document's own text --
# see deliverables/session00/11_addendum_csv_v1.1_revision_plan_2026-11-08.md
# §6 ("Danh sách 4 mã ... có phải danh sách cuối cùng").
HOLD_FLAG_CODES = frozenset({
    "EPISODE_BOUNDARY_REVIEW", "OVERLAPPING_WINDOWS",
    "SAME_DAY_ORDER_UNCLEAR", "BASELINE_CARE_PLAN",
})

_SUBJECT_CASE_STATUS = "対象"


def _parse_flags(context_review_flags: str) -> set[str]:
    """B17 is free-text pass-through with no enforced separator yet (no
    validation exists against dictionaries/D5_context_flags.csv either) --
    split defensively on common delimiters rather than assuming one."""
    return {tok.strip().upper() for tok in re.split(r"[;,/\s]+", context_review_flags or "") if tok.strip()}


def has_hold_flag(context_review_flags: str) -> bool:
    """True if B17 contains any of the 4 集計保留フラグ codes (v1.1 §5)."""
    return bool(_parse_flags(context_review_flags) & HOLD_FLAG_CODES)


def composite_event_30d(admission_30d: str, transport_30d: str, death_30d: str) -> str:
    """複合急変 3値規則 (CSV Design Guide v1.1 §9, verbatim):
    ① あり -- admission/transport/death のいずれかが「あり」（他が不明でも可）。
    ② なし -- 3転帰すべて「なし」。
    ③ 確認不能 -- otherwise.
    See module docstring for the one refinement (reject-loop) deliberately
    not modelled -- a fully-"N" episode is always ② here."""
    values = (admission_30d, transport_30d, death_30d)
    if "Y" in values:
        return "あり"
    if all(v == "N" for v in values):
        return "なし"
    return "確認不能"


def split_by_hold_flag(episodes: list[dict]) -> tuple[list[dict], list[dict]]:
    """Per v1.1 §5/§9: episodes with a 集計保留フラグ in B17 are excluded
    from the official denominator T and reported separately, never dropped
    silently. Returns (included_in_T, held_back)."""
    included, held = [], []
    for ep in episodes:
        (held if has_hold_flag(ep.get("context_review_flags", "")) else included).append(ep)
    return included, held


def _rate(numerator: int, denominator: int) -> float | None:
    return (numerator / denominator * 100) if denominator else None


def compute_outcome_rates(episodes: list[dict]) -> dict:
    """episodes: supplementary-export-shaped dicts (one per episode_id).

    Per v1.1 §9: only case_status == "対象" episodes enter the official
    denominator T ("対象エピソード総数T"); among those, episodes carrying a
    集計保留フラグ are excluded from T and counted in held_back_count
    instead (see split_by_hold_flag), not discarded.

    割合 (per v1.1 §9, verbatim): 複合あり÷（複合あり＋複合なし）×100；
    確認不能割合は全対象件数（= T）を分母；個別転帰（入院/搬送/死亡）は各々
    あり÷（あり＋なし）で別計算。
    """
    subject = [e for e in episodes if e.get("case_status") == _SUBJECT_CASE_STATUS]
    included, held = split_by_hold_flag(subject)

    composite = [
        composite_event_30d(e.get("admission_30d", ""), e.get("transport_30d", ""), e.get("death_30d", ""))
        for e in included
    ]
    n_ari, n_nashi, n_fukaku = composite.count("あり"), composite.count("なし"), composite.count("確認不能")

    def _individual_rate(key: str) -> float | None:
        vals = [e.get(key, "") for e in included]
        return _rate(vals.count("Y"), vals.count("Y") + vals.count("N"))

    return {
        "denominator_t": len(included),
        "held_back_count": len(held),
        "composite_ari": n_ari, "composite_nashi": n_nashi, "composite_fukaku": n_fukaku,
        "composite_rate_percent": _rate(n_ari, n_ari + n_nashi),
        "fukaku_rate_percent": _rate(n_fukaku, len(included)),
        "admission_rate_percent": _individual_rate("admission_30d"),
        "transport_rate_percent": _individual_rate("transport_30d"),
        "death_rate_percent": _individual_rate("death_30d"),
    }
