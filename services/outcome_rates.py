"""Outcome-level aggregation per CSV設計説明書v1.3.1 §8 ("集計への受け渡し").

Operates only on reviewer-filled episode rows (one dict per episode_id,
B column names from models.csv_schemas.MANUAL_REVIEW_COLUMNS plus C01
qc_status) -- never on raw DB rows, and never computes case_status/
day0_date/outcome_type itself (CLAUDE.md muc 3): those are always a
human reviewer's values, taken as given, not re-derived here.

v1.3.1 replaces the old v1.1 B17 "集計保留フラグ" mechanism (4 free-text
codes on an already-対象 episode) with a plain third B02 case_status
value, 保留, that is mutually exclusive with 対象/対象外 -- so there is no
longer a flag column to parse, just a value to filter on. See
dictionaries/D6_case_status_reasons.csv for the (still-DRAFT) B03 reason
taxonomy and its explicit "保留 rows excluded from the denominator" rule.
"""
from __future__ import annotations

_CASE_STATUS_TARGET = "対象"
_CASE_STATUS_HELD = "保留"
_QC_OK = frozenset({"問題なし", "修正確認済"})

_PRESENT, _ABSENT, _UNKNOWN = "あり", "なし", "不明"


def composite_event_30d(admission_30d: str, transport_30d: str, death_30d: str) -> str:
    """複合転帰 3値規則 (CSV設計説明書v1.3.1 §8, verbatim):
    あり -- 3つの転帰のどれかが「あり」（ほかが「不明」でもよい）。
    なし -- 3つの転帰がすべて「なし」。
    確認不能 -- 上のどちらにも当たらない。"""
    values = (admission_30d, transport_30d, death_30d)
    if _PRESENT in values:
        return _PRESENT
    if all(v == _ABSENT for v in values):
        return _ABSENT
    return "確認不能"


def split_target_held_excluded(episodes: list[dict]) -> tuple[list[dict], list[dict], list[dict]]:
    """B02 (case_status) partitions episodes into 対象/保留/対象外. 保留 rows
    are reported separately and never enter the deterioration-rate
    denominator (CSV設計説明書v1.3.1 §8, 診療録レビューの判定基準v1.3.1 §4)."""
    target, held, excluded = [], [], []
    for ep in episodes:
        status = ep.get("case_status", "")
        if status == _CASE_STATUS_TARGET:
            target.append(ep)
        elif status == _CASE_STATUS_HELD:
            held.append(ep)
        else:
            excluded.append(ep)
    return target, held, excluded


def _qc_passed(episodes: list[dict]) -> list[dict]:
    """集計に使う行 (CSV設計説明書v1.3.1 §8): B02＝対象で、C01が「問題なし」
    または「修正確認済」の行だけ。"""
    return [ep for ep in episodes if ep.get("qc_status") in _QC_OK]


def _unplanned_only_admission(episode: dict) -> str:
    """B12 (admission_type) only has meaning when B10=あり. Definition 2
    (手順書v1.3.1 §6.1): a PLANNED admission doesn't count as an event; an
    admission whose type is unrecorded is 不明, not あり (never assume
    unplanned by default)."""
    if episode.get("admission_30d") != _PRESENT:
        return episode.get("admission_30d", "")
    admission_type = episode.get("admission_type")
    if admission_type == "予定外":
        return _PRESENT
    if admission_type == "予定":
        return _ABSENT
    return "不明"


def _rate(numerator: int, denominator: int) -> float | None:
    return (numerator / denominator * 100) if denominator else None


def _individual_rate(episodes: list[dict], key: str) -> float | None:
    vals = [e.get(key, "") for e in episodes]
    return _rate(vals.count(_PRESENT), vals.count(_PRESENT) + vals.count(_ABSENT))


def compute_outcome_rates(episodes: list[dict]) -> dict:
    """episodes: reviewer-filled dicts, one per episode_id (B01-B22 + C01).

    Mục 5 #1 (addendum 15) is still open: whether 入院 (admission_30d) for
    the official deterioration-rate denominator means "all admissions" or
    "unplanned only" (B12=予定外) has not been decided by the project
    owner/PI. 手順書v1.3.1 §6.1 itself says to compute both until that is
    settled -- so this function always returns both, clearly labeled, and
    never silently picks one.
    """
    target, held, excluded = split_target_held_excluded(episodes)
    included = _qc_passed(target)

    composite_all = [
        composite_event_30d(e.get("admission_30d", ""), e.get("transport_30d", ""), e.get("death_30d", ""))
        for e in included
    ]
    unplanned_admission = [_unplanned_only_admission(e) for e in included]
    composite_unplanned_only = [
        composite_event_30d(a, e.get("transport_30d", ""), e.get("death_30d", ""))
        for a, e in zip(unplanned_admission, included)
    ]

    def _summary(composite: list[str]) -> dict:
        n_ari, n_nashi, n_fukaku = composite.count(_PRESENT), composite.count(_ABSENT), composite.count("確認不能")
        return {
            "composite_ari": n_ari, "composite_nashi": n_nashi, "composite_fukaku": n_fukaku,
            "composite_rate_percent": _rate(n_ari, n_ari + n_nashi),
            "fukaku_rate_percent": _rate(n_fukaku, len(included)),
        }

    return {
        "denominator_t": len(included),
        "held_back_count": len(held),
        "excluded_count": len(excluded),
        "qc_not_passed_count": len(target) - len(included),
        # 入院の定義1: すべての入院 (手順書v1.3.1 §6.1)
        "all_admissions": _summary(composite_all),
        # 入院の定義2: 予定外の入院だけ (手順書v1.3.1 §6.1) -- Mục 5 #1 open
        "unplanned_admissions_only": _summary(composite_unplanned_only),
        "admission_rate_percent": _individual_rate(included, "admission_30d"),
        "transport_rate_percent": _individual_rate(included, "transport_30d"),
        "death_rate_percent": _individual_rate(included, "death_30d"),
    }
