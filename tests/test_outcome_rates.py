"""Tests for services/outcome_rates.py -- the 複合急変 (composite outcome)
classification and 集計保留フラグ denominator-T exclusion from CSV Design
Guide v1.1 §5/§9. Small synthetic fixtures only."""
from services.outcome_rates import (
    HOLD_FLAG_CODES, compute_outcome_rates, composite_event_30d, has_hold_flag, split_by_hold_flag,
)


def _ep(**overrides):
    row = {
        "episode_id": "EP1", "case_status": "対象",
        "admission_30d": "", "transport_30d": "", "death_30d": "",
        "context_review_flags": "",
    }
    row.update(overrides)
    return row


def test_composite_ari_if_any_event_y_even_with_others_unknown():
    assert composite_event_30d("Y", "不明", "不明") == "あり"
    assert composite_event_30d("N", "N", "Y") == "あり"


def test_composite_nashi_if_all_three_n():
    assert composite_event_30d("N", "N", "N") == "なし"


def test_composite_fukaku_otherwise():
    assert composite_event_30d("不明", "N", "N") == "確認不能"
    assert composite_event_30d("", "", "") == "確認不能"


def test_has_hold_flag_matches_any_of_the_4_codes():
    assert has_hold_flag("EPISODE_BOUNDARY_REVIEW") is True
    assert has_hold_flag("PRIOR_INPATIENT_ABX") is False
    assert has_hold_flag("") is False


def test_has_hold_flag_handles_multiple_values_with_common_separators():
    assert has_hold_flag("PRIOR_INPATIENT_ABX, BASELINE_CARE_PLAN") is True
    assert has_hold_flag("SOURCE_CONFLICT; OVERLAPPING_WINDOWS") is True
    assert has_hold_flag("SAME_DAY_ORDER_UNCLEAR/TRANSFERRED_DOCUMENT") is True


def test_exactly_4_hold_flag_codes():
    assert HOLD_FLAG_CODES == {
        "EPISODE_BOUNDARY_REVIEW", "OVERLAPPING_WINDOWS", "SAME_DAY_ORDER_UNCLEAR", "BASELINE_CARE_PLAN",
    }


def test_split_by_hold_flag_separates_without_dropping():
    episodes = [_ep(episode_id="EP1", context_review_flags=""),
                _ep(episode_id="EP2", context_review_flags="BASELINE_CARE_PLAN")]
    included, held = split_by_hold_flag(episodes)
    assert [e["episode_id"] for e in included] == ["EP1"]
    assert [e["episode_id"] for e in held] == ["EP2"]


def test_compute_outcome_rates_excludes_non_subject_and_held_back():
    episodes = [
        _ep(episode_id="EP1", admission_30d="Y", transport_30d="N", death_30d="N"),
        _ep(episode_id="EP2", admission_30d="N", transport_30d="N", death_30d="N"),
        _ep(episode_id="EP3", admission_30d="N", transport_30d="N", death_30d="N", case_status="対象外"),
        _ep(episode_id="EP4", admission_30d="Y", transport_30d="N", death_30d="N",
            context_review_flags="OVERLAPPING_WINDOWS"),
    ]
    result = compute_outcome_rates(episodes)
    assert result["denominator_t"] == 2  # EP1, EP2 only -- EP3 not 対象, EP4 held back
    assert result["held_back_count"] == 1
    assert result["composite_ari"] == 1
    assert result["composite_nashi"] == 1
    assert result["composite_rate_percent"] == 50.0
    assert result["admission_rate_percent"] == 50.0


def test_compute_outcome_rates_empty_denominator_returns_none_not_crash():
    result = compute_outcome_rates([])
    assert result["denominator_t"] == 0
    assert result["composite_rate_percent"] is None
    assert result["fukaku_rate_percent"] is None
