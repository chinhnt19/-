"""V01-V09 input-check rules, CSV設計説明書v1.3.1 §7 ("入力の点検").

These detect data-entry problems in an already reviewer-filled unified
CSV row -- they never judge whether a case_status/Day0/outcome value is
*correct*, only whether the row is internally consistent (CLAUDE.md mục
3: "検索ツールでは、次の処理をしない: ... 空欄や「記載なし」を、転帰の「なし」
に変える" -- this module does not decide C01/qc_status either; it only
surfaces findings for whoever fills C01/C02 to act on. The secondary
reviewer (二次確認, C01/C02) is always the one who sets qc_status; this
module's output is their input, not a replacement for it.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from models.csv_schemas import (
    ADMISSION_TYPE, CASE_STATUS, DEATH_PLACE, EHR_SOURCE, FOLLOWUP_STATUS,
    FOLLOWUP_UNKNOWN_REASON, PRESENT_ABSENT_UNKNOWN, QC_ISSUE, QC_STATUS,
    RESIDENCE_TYPE, ROUTE_CLASS, YES_NO_UNKNOWN,
)

# CSV設計説明書v1.3.1 §4.2: columns required (non-blank) when B02=対象.
REQUIRED_WHEN_TARGET: tuple[str, ...] = (
    "day0_date", "day0_evidence", "last_infusion_date", "infusion_days",
    "home_completed", "residence_type", "admission_30d", "transport_30d",
    "death_30d", "followup_status",
)

# Columns whose value list is restricted to a fixed enum (V07). Multi-
# valued columns (route_class, qc_issue) are checked per-"|"-separated token.
_SINGLE_VALUE_ENUMS: dict[str, tuple[str, ...]] = {
    "ehr_source": EHR_SOURCE,
    "case_status": CASE_STATUS,
    "home_completed": YES_NO_UNKNOWN,
    "residence_type": RESIDENCE_TYPE,
    "admission_30d": PRESENT_ABSENT_UNKNOWN,
    "admission_type": ADMISSION_TYPE,
    "transport_30d": PRESENT_ABSENT_UNKNOWN,
    "death_30d": PRESENT_ABSENT_UNKNOWN,
    "death_place": DEATH_PLACE,
    "followup_status": FOLLOWUP_STATUS,
    "followup_unknown_reason": FOLLOWUP_UNKNOWN_REASON,
    "qc_status": QC_STATUS,
}
_MULTI_VALUE_ENUMS: dict[str, tuple[str, ...]] = {
    "route_class": ROUTE_CLASS,
    "qc_issue": QC_ISSUE,
}

_TARGET = "対象"
_PRESENT = "あり"


@dataclass(frozen=True)
class QcFinding:
    check_id: str  # V01-V09
    severity: str  # "エラー" | "警告"
    message: str


def _parse_date(s: str) -> date | None:
    try:
        return date.fromisoformat(s) if s else None
    except ValueError:
        return None


def check_row(row: dict, all_episode_ids: list[str] | None = None) -> list[QcFinding]:
    """Row-level checks (V01-V05, V07-V09). Pass `all_episode_ids` (every
    episode_id across the file being checked) to also get V06 (duplicate)
    for this row; omit it to skip V06 (e.g. when checking a single row in
    isolation)."""
    findings: list[QcFinding] = []
    is_target = row.get("case_status") == _TARGET

    # V01: required-when-target columns must not be blank.
    if is_target:
        blanks = [c for c in REQUIRED_WHEN_TARGET if not row.get(c)]
        if blanks:
            findings.append(QcFinding("V01", "エラー", f"B02=対象 だが必須列が空欄: {', '.join(blanks)}"))

    # V02: admission/transport/death_30d = あり だが日付が空欄.
    for present_col, date_col in (("admission_30d", "admission_date"),
                                   ("transport_30d", "transport_date"),
                                   ("death_30d", "death_date")):
        if row.get(present_col) == _PRESENT and not row.get(date_col):
            findings.append(QcFinding("V02", "エラー", f"{present_col}=あり だが {date_col} が空欄"))

    # V03/V04: date-ordering checks, only meaningful once day0_date exists.
    day0 = _parse_date(row.get("day0_date", ""))
    if day0 is not None:
        day30 = day0 + timedelta(days=30)
        for date_col in ("admission_date", "transport_date", "death_date"):
            d = _parse_date(row.get(date_col, ""))
            if d is not None and (d < day0 or d > day30):
                findings.append(QcFinding("V03", "エラー", f"{date_col}={d} が Day0({day0})〜Day30({day30}) の外"))
        last_infusion = _parse_date(row.get("last_infusion_date", ""))
        if last_infusion is not None and last_infusion < day0:
            findings.append(QcFinding("V04", "エラー", f"last_infusion_date={last_infusion} が day0_date={day0} より前"))

    # V05: 3 outcomes all なし だが followup_status が一部不明/追跡不能.
    outcomes = (row.get("admission_30d"), row.get("transport_30d"), row.get("death_30d"))
    if all(v == "なし" for v in outcomes) and row.get("followup_status") in ("一部不明", "追跡不能"):
        findings.append(QcFinding("V05", "エラー", "3転帰すべてなしだがfollowup_statusが一部不明/追跡不能"))

    # V06: duplicate episode_id (only if the caller gave us the full list).
    if all_episode_ids is not None:
        eid = row.get("episode_id", "")
        if eid and all_episode_ids.count(eid) > 1:
            findings.append(QcFinding("V06", "エラー", f"episode_id={eid} が重複"))

    # V07: enum columns restricted to a fixed value list.
    for col, allowed in _SINGLE_VALUE_ENUMS.items():
        val = row.get(col, "")
        if val and val not in allowed:
            findings.append(QcFinding("V07", "エラー", f"{col}={val!r} は値の一覧にない"))
    for col, allowed in _MULTI_VALUE_ENUMS.items():
        val = row.get(col, "")
        if val:
            bad = [tok for tok in val.split("|") if tok and tok not in allowed]
            if bad:
                findings.append(QcFinding("V07", "エラー", f"{col} に値の一覧にないトークン: {bad}"))

    # V08: 対象外/保留 だが case_reason(B03) が空欄.
    if row.get("case_status") in ("対象外", "保留") and not row.get("case_reason"):
        findings.append(QcFinding("V08", "警告", "case_status=対象外/保留 だが case_reason が空欄"))

    # V09: followup_status 一部不明/追跡不能 だが last_followup_date/followup_unknown_reason が空欄.
    if row.get("followup_status") in ("一部不明", "追跡不能"):
        blanks = [c for c in ("last_followup_date", "followup_unknown_reason") if not row.get(c)]
        if blanks:
            findings.append(QcFinding("V09", "警告", f"followup_status=一部不明/追跡不能 だが空欄: {', '.join(blanks)}"))

    return findings


def check_all(rows: list[dict]) -> dict[int, list[QcFinding]]:
    """Checks every row, including V06 (duplicate episode_id) across the
    whole file. Returns {row_index: [findings]} -- rows with no findings
    are omitted."""
    all_episode_ids = [r.get("episode_id", "") for r in rows]
    result: dict[int, list[QcFinding]] = {}
    for i, row in enumerate(rows):
        findings = check_row(row, all_episode_ids)
        if findings:
            result[i] = findings
    return result
