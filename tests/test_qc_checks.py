"""Tests for exports/qc_checks.py -- V01-V09 input-check rules
(CSV設計説明書v1.3.1 §7)."""
from exports.qc_checks import check_all, check_row


def _row(**overrides):
    row = {
        "case_status": "対象", "case_reason": "",
        "day0_date": "2026-05-03", "day0_evidence": "ref1",
        "last_infusion_date": "2026-05-10", "infusion_days": "5",
        "home_completed": "はい", "residence_type": "自宅",
        "admission_30d": "なし", "admission_date": "", "admission_type": "",
        "transport_30d": "なし", "transport_date": "",
        "death_30d": "なし", "death_date": "", "death_place": "",
        "followup_status": "完了", "last_followup_date": "", "followup_unknown_reason": "",
        "ehr_source": "NAHT", "route_class": "点滴静注", "qc_status": "", "qc_issue": "",
        "episode_id": "EP1",
    }
    row.update(overrides)
    return row


def test_v01_required_when_target_blank():
    findings = check_row(_row(day0_date=""))
    assert any(f.check_id == "V01" for f in findings)


def test_v01_not_triggered_when_not_target():
    findings = check_row(_row(case_status="対象外", day0_date="", day0_evidence="", case_reason="在宅での投与なし"))
    assert not any(f.check_id == "V01" for f in findings)


def test_v02_present_without_date():
    findings = check_row(_row(admission_30d="あり", admission_date=""))
    assert any(f.check_id == "V02" for f in findings)


def test_v03_date_outside_day0_day30_window():
    findings = check_row(_row(admission_30d="あり", admission_date="2026-06-15"))  # > Day30
    assert any(f.check_id == "V03" for f in findings)


def test_v03_date_within_window_ok():
    findings = check_row(_row(admission_30d="あり", admission_date="2026-05-20"))  # within Day0-30
    assert not any(f.check_id == "V03" for f in findings)


def test_v04_last_infusion_before_day0():
    findings = check_row(_row(last_infusion_date="2026-05-01"))  # day0_date is 2026-05-03
    assert any(f.check_id == "V04" for f in findings)


def test_v05_all_absent_but_followup_incomplete():
    findings = check_row(_row(followup_status="追跡不能", last_followup_date="2026-05-05", followup_unknown_reason="その他"))
    assert any(f.check_id == "V05" for f in findings)


def test_v06_duplicate_episode_id():
    rows = [_row(episode_id="EP1"), _row(episode_id="EP1")]
    result = check_all(rows)
    assert all(any(f.check_id == "V06" for f in fs) for fs in result.values())


def test_v07_enum_violation():
    findings = check_row(_row(home_completed="たぶん"))
    assert any(f.check_id == "V07" for f in findings)


def test_v07_multi_value_enum_violation():
    findings = check_row(_row(route_class="点滴静注|経口"))
    assert any(f.check_id == "V07" and "route_class" in f.message for f in findings)


def test_v08_excluded_without_reason():
    findings = check_row(_row(case_status="対象外", case_reason="", day0_date="", day0_evidence=""))
    assert any(f.check_id == "V08" for f in findings)


def test_v09_incomplete_followup_without_detail():
    findings = check_row(_row(followup_status="一部不明", last_followup_date="", followup_unknown_reason=""))
    assert any(f.check_id == "V09" for f in findings)


def test_clean_row_has_no_findings():
    findings = check_row(_row())
    assert findings == []
