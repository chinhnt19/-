"""Tests for services/outcome_rates.py -- the v1.3.1 複合転帰 (composite
outcome) classification and B02=保留 denominator exclusion
(CSV設計説明書v1.3.1 §8). Small synthetic fixtures only.

v1.0/v1.1 used Y/N/UNCONFIRMED tokens and a B17 "集計保留フラグ" free-text
column; v1.3.1 uses literal あり/なし/不明 enum values and a plain B02=保留
case_status -- this file replaces the old Y/N-token tests."""
from services.outcome_rates import compute_outcome_rates, composite_event_30d, split_target_held_excluded


def _ep(**overrides):
    row = {
        "episode_id": "EP1", "case_status": "対象", "qc_status": "問題なし", "admission_type": "予定外",
        "admission_30d": "", "transport_30d": "", "death_30d": "",
    }
    row.update(overrides)
    return row


def test_composite_ari_if_any_event_present_even_with_others_unknown():
    assert composite_event_30d("あり", "不明", "不明") == "あり"
    assert composite_event_30d("なし", "なし", "あり") == "あり"


def test_composite_nashi_if_all_three_absent():
    assert composite_event_30d("なし", "なし", "なし") == "なし"


def test_composite_fukaku_otherwise():
    assert composite_event_30d("不明", "なし", "なし") == "確認不能"
    assert composite_event_30d("", "", "") == "確認不能"


def test_split_target_held_excluded_three_way():
    episodes = [
        _ep(episode_id="EP1", case_status="対象"),
        _ep(episode_id="EP2", case_status="保留"),
        _ep(episode_id="EP3", case_status="対象外"),
    ]
    target, held, excluded = split_target_held_excluded(episodes)
    assert [e["episode_id"] for e in target] == ["EP1"]
    assert [e["episode_id"] for e in held] == ["EP2"]
    assert [e["episode_id"] for e in excluded] == ["EP3"]


def test_compute_outcome_rates_excludes_non_target_held_and_qc_failed():
    episodes = [
        _ep(episode_id="EP1", admission_30d="あり", transport_30d="なし", death_30d="なし", admission_type="予定外"),
        _ep(episode_id="EP2", admission_30d="なし", transport_30d="なし", death_30d="なし"),
        _ep(episode_id="EP3", admission_30d="なし", transport_30d="なし", death_30d="なし", case_status="対象外"),
        _ep(episode_id="EP4", admission_30d="あり", transport_30d="なし", death_30d="なし", case_status="保留"),
        _ep(episode_id="EP5", admission_30d="あり", transport_30d="なし", death_30d="なし", qc_status="要修正"),
    ]
    result = compute_outcome_rates(episodes)
    assert result["denominator_t"] == 2  # EP1, EP2 only
    assert result["held_back_count"] == 1
    assert result["excluded_count"] == 1
    assert result["qc_not_passed_count"] == 1
    assert result["all_admissions"]["composite_ari"] == 1
    assert result["all_admissions"]["composite_nashi"] == 1
    assert result["all_admissions"]["composite_rate_percent"] == 50.0
    assert result["admission_rate_percent"] == 50.0


def test_unplanned_only_admission_definition_differs_from_all():
    episodes = [
        _ep(episode_id="EP1", admission_30d="あり", admission_type="予定", transport_30d="なし", death_30d="なし"),
        _ep(episode_id="EP2", admission_30d="なし", transport_30d="なし", death_30d="なし"),
    ]
    result = compute_outcome_rates(episodes)
    # Definition 1 (all admissions): EP1 counts as あり.
    assert result["all_admissions"]["composite_ari"] == 1
    # Definition 2 (unplanned only): EP1's planned admission does not count.
    assert result["unplanned_admissions_only"]["composite_ari"] == 0
    assert result["unplanned_admissions_only"]["composite_nashi"] == 2


def test_compute_outcome_rates_empty_denominator_returns_none_not_crash():
    result = compute_outcome_rates([])
    assert result["denominator_t"] == 0
    assert result["all_admissions"]["composite_rate_percent"] is None
    assert result["all_admissions"]["fukaku_rate_percent"] is None
