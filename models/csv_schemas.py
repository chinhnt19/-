"""Column names and order for the v1.3.1 unified CSV (A=17 tool columns +
B=22 reviewer columns + C=2 QC columns = 41) and the separate covariate
file, per `後ろ向き集計 CSV設計説明書v1.3.1.docx` §4-5.

This replaces the v1.0 "6 CSV" model (Candidate + 3 Evidence + Manual
Review + Outcome, modeled on the Q10/Q20/Q30 3-axis combination matrix).
The column names, order and enum values below are copied verbatim from
the source doc's tables -- the dashboard/export code must never invent a
different name, order, or enum value than what is listed here.

Columns whose value list still carries 未承認/DRAFT in the source (B03
reason codes, A17/B05/B22 evidence_ref format, A16 dictionary version,
BOM) are implemented with the dictionary's own draft values
(dictionaries/D6_case_status_reasons.csv) -- never silently treated as
approved. See deliverables/session00/15_addendum_v1.3.1_migration_plan_
2026-11-11.md Mục 5 for the open items.
"""
from __future__ import annotations

# A: 17 columns the search tool outputs for each candidate (one row = one
# contiguous run of billed months per facility+patient; CSV設計説明書 §4.1).
CANDIDATE_COLUMNS: tuple[str, ...] = (
    "extract_batch_id", "candidate_id", "facility_id", "patient_local_id",
    "ehr_source", "age_at_start", "sex", "first_record_month",
    "last_record_month", "record_months", "drug_names", "drug_codes",
    "route_class", "diagnosis_names", "diagnosis_codes",
    "diagnosis_categories", "evidence_ref",
)

# B: 22 columns the chart reviewer fills in per treatment episode (CSV設計
# 説明書 §4.2). One candidate row may be copied into >=1 episode rows when
# the 14-day rule splits it (B01 gets a "candidate_id-N" suffix each time).
MANUAL_REVIEW_COLUMNS: tuple[str, ...] = (
    "episode_id", "case_status", "case_reason", "day0_date", "day0_evidence",
    "last_infusion_date", "infusion_days", "home_completed", "residence_type",
    "admission_30d", "admission_date", "admission_type", "admission_facility",
    "transport_30d", "transport_date", "death_30d", "death_date",
    "death_place", "followup_status", "last_followup_date",
    "followup_unknown_reason", "outcome_evidence_ref",
)

# C: 2 QC columns (CSV設計説明書 §4.3 / §7 V01-V09).
QC_COLUMNS: tuple[str, ...] = ("qc_status", "qc_issue")

# The full 41-column unified CSV, in A -> B -> C order.
UNIFIED_CSV_COLUMNS: tuple[str, ...] = CANDIDATE_COLUMNS + MANUAL_REVIEW_COLUMNS + QC_COLUMNS

# Covariate file: separate from the main CSV, one row per
# (episode_id, covariate) pair (CSV設計説明書 §5).
COVARIATE_COLUMNS: tuple[str, ...] = ("episode_id", "covariate", "value", "recorded", "source")

COVARIATE_ITEMS: tuple[str, ...] = (
    "オピオイド", "中枢性鎮咳薬", "抗精神病薬", "食事摂取量", "COPD",
    "心不全", "脳血管障害", "要介護度", "エアマット",
)

# ---- Enum values, verbatim from CSV設計説明書v1.3.1 §4 ---------------------
# A05 ehr_source
EHR_SOURCE = ("NAHT", "HOMIS")
# A13 route_class (multi-valued, "|"-joined)
ROUTE_CLASS = ("静注", "点滴静注")
# B02 case_status
CASE_STATUS_TARGET = "対象"
CASE_STATUS_EXCLUDED = "対象外"
CASE_STATUS_HELD = "保留"
CASE_STATUS = (CASE_STATUS_TARGET, CASE_STATUS_EXCLUDED, CASE_STATUS_HELD)
# B03 case_reason -- draft vocabulary, see dictionaries/D6_case_status_reasons.csv
# (Mục 5 #3 of addendum 15: this list is not yet formally approved).
YES_NO_UNKNOWN = ("はい", "いいえ", "不明")  # B08 home_completed
RESIDENCE_TYPE = ("自宅", "施設", "不明")  # B09
PRESENT_ABSENT_UNKNOWN = ("あり", "なし", "不明")  # B10/B14/B16 admission/transport/death_30d
ADMISSION_TYPE = ("予定", "予定外", "不明")  # B12
DEATH_PLACE = ("自宅", "施設", "病院", "不明")  # B18
FOLLOWUP_STATUS = ("完了", "一部不明", "追跡不能")  # B19
FOLLOWUP_UNKNOWN_REASON = ("他院へ転院", "連携記録なし", "その他")  # B21
# C01 qc_status
QC_STATUS = ("未確認", "問題なし", "要修正", "修正確認済")
# C02 qc_issue (multi-valued, "|"-joined)
QC_ISSUE = ("空欄あり", "日付の矛盾", "根拠なし", "転記ミス")
# Covariate file `recorded`
RECORDED = ("あり", "なし")

MULTI_VALUE_SEPARATOR = "|"

# The V01-V09 input-check rules (CSV設計説明書 §7) are implemented in
# exports/ (next commit), not here -- this module only fixes column
# names/order/enum values.
