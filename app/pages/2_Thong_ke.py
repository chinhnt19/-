"""Thống kê candidate (model v1.3.1) + tỉ lệ転帰 30 ngày (sau khi upload file
review đã điền B/C)."""
import sys
from collections import Counter
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent.parent
_ROOT_DIR = _APP_DIR.parent
for _p in (_APP_DIR, _ROOT_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import pandas as pd
import streamlit as st

from _bootstrap import known_clinic_ids
from rules.clinic_tool_mapping import clinic_group
from services.i18n import language_selector, t
from services.outcome_rates import compute_outcome_rates

st.set_page_config(page_title="Thống kê — AGRI CARE", layout="wide")
language_selector()
st.title(t("stats.title"))

if "last_run_result" not in st.session_state:
    st.warning(t("common.no_run_warning"))
    st.page_link("pages/1_Tim_kiem.py", label=t("common.link_to_search"), icon="🔎")
    st.stop()

result = st.session_state.last_run_result
df = pd.DataFrame(result.candidates)
if df.empty:
    st.info(t("stats.no_candidates"))
    st.stop()

df[t("col.group")] = df["facility_id"].map(lambda c: clinic_group(c, known_clinic_ids()))

st.subheader(t("stats.overview_header"))
c1, c2, c3 = st.columns(3)
c1.metric(t("stats.metric_candidates"), len(df))
c2.metric(t("stats.metric_patients"), df["patient_local_id"].nunique())
c3.metric(t("stats.metric_facilities"), df["facility_id"].nunique())

st.divider()
st.subheader(t("stats.by_group_header"))
by_group = df.groupby(t("col.group")).size().rename(t("stats.metric_candidates"))
st.bar_chart(by_group)

st.divider()
st.subheader(t("stats.by_route_header"))
route_counts = df["route_class"].value_counts()
st.bar_chart(route_counts)
st.caption(t("stats.route_caption"))

st.divider()
st.subheader(t("stats.length_header"))
st.bar_chart(df["record_months"].value_counts().sort_index())

st.divider()
st.subheader(t("stats.diagnosis_header"))
st.caption(t("stats.diagnosis_caption"))
cat_counter: Counter[str] = Counter()
state_counter: Counter[str] = Counter()
for cats in df["diagnosis_categories"]:
    for token in (cats or "").split("|"):
        if ":" not in token:
            continue
        cat, state = token.split(":", 1)
        cat_counter[cat] += 1
        state_counter[state] += 1
if cat_counter:
    cat_df = pd.DataFrame(
        sorted(cat_counter.items(), key=lambda kv: -kv[1]), columns=["区分", t("stats.metric_candidates")],
    )
    st.dataframe(cat_df, hide_index=True, width="stretch")
    a_count, s_count = state_counter.get("A", 0), state_counter.get("S", 0)
    st.caption(t("stats.diagnosis_counts_caption", a=a_count, s=s_count))
else:
    st.caption(t("stats.no_diagnosis"))

st.divider()
st.subheader(t("stats.unconfirmed_header"))
col_item, col_status = t("stats.table_col_item"), t("stats.table_col_status")
st.table(pd.DataFrame([
    {col_item: "A06 age_at_start / A07 sex", col_status: t("stats.row1_status")},
    {col_item: "病名 転帰日 (outcome date)", col_status: t("stats.row2_status")},
    {col_item: "D4 P08/P11 (入院中手技料/中心静脈注射)", col_status: t("stats.row3_status")},
    {col_item: "disease_code LIKE 'ZZZ%'", col_status: t("stats.row4_status")},
]), width="stretch")

st.divider()
st.subheader(t("stats.outcome_header"))
st.caption(t("stats.outcome_decision_caption"))
imported = st.session_state.get("imported_review_df")
if imported is not None and (imported.get("case_status", pd.Series(dtype=str)) != "").any():
    rates = compute_outcome_rates(imported.to_dict("records"))

    def _pct(v):
        return "—" if v is None else f"{v:.1f}%"

    o1, o2, o3, o4 = st.columns(4)
    o1.metric(t("stats.metric_denominator"), rates["denominator_t"])
    o2.metric(t("stats.metric_held_back"), rates["held_back_count"])
    o3.metric("対象外", rates["excluded_count"])
    o4.metric(t("stats.metric_not_qc"), rates["qc_not_passed_count"])

    tab_all, tab_unplanned = st.tabs([t("stats.tab_all_admissions"), t("stats.tab_unplanned")])
    for tab, key in ((tab_all, "all_admissions"), (tab_unplanned, "unplanned_admissions_only")):
        with tab:
            s = rates[key]
            r1, r2, r3 = st.columns(3)
            r1.metric("複合転帰 あり", s["composite_ari"])
            r2.metric("複合転帰 なし", s["composite_nashi"])
            r3.metric("確認不能", s["composite_fukaku"])
            r4, r5 = st.columns(2)
            r4.metric("複合転帰 割合", _pct(s["composite_rate_percent"]))
            r5.metric("確認不能 割合", _pct(s["fukaku_rate_percent"]))

    r6, r7, r8 = st.columns(3)
    r6.metric("入院 割合", _pct(rates["admission_rate_percent"]))
    r7.metric("救急搬送 割合", _pct(rates["transport_rate_percent"]))
    r8.metric("死亡 割合", _pct(rates["death_rate_percent"]))
    st.caption(t("stats.ratio_formula_caption"))
else:
    st.info(t("stats.no_review_uploaded"))

st.page_link("pages/3_Danh_sach_ung_vien.py", label=t("search.link_candidates"), icon="📋")
