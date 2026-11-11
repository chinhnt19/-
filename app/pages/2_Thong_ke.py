"""Block 4 -- Candidate Statistics."""
import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent.parent
_ROOT_DIR = _APP_DIR.parent
for _p in (_APP_DIR, _ROOT_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import pandas as pd
import streamlit as st

from _bootstrap import known_clinic_ids
from exports.supplementary_export import build_supplementary_export
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

df[t("col.group")] = df["clinic_id"].map(lambda c: clinic_group(c, known_clinic_ids()))

st.subheader(t("stats.matrix_header"))
st.caption(t("stats.matrix_caption"))
cell_order = ["A_only", "B_only", "C_only", "A_and_B(=Q30)", "A_and_C_not_B", "B_and_C_not_A", "A_and_B_and_C"]
pivot = df.pivot_table(index="combination_cell", columns=t("col.group"), values="candidate_id", aggfunc="count", fill_value=0)
pivot = pivot.reindex(cell_order, fill_value=0)
pivot[t("stats.col_total")] = pivot.sum(axis=1)
st.table(pivot)

c1, c2, c3 = st.columns(3)
c1.metric(t("stats.metric_total_a"), int((df["in_set_a_q10"] == "Y").sum()))
c2.metric(t("stats.metric_total_b"), int((df["in_set_b_q20"] == "Y").sum()))
c3.metric(t("stats.metric_total_c"), int((df["in_set_c_wide_qc1"] == "Y").sum()))

st.caption(t("stats.qc2_caption", n=int((df["in_set_c_narrow_qc2"] == "UNCONFIRMED").sum())))

st.divider()
st.subheader(t("stats.d3_header"))
d3_counts = df.loc[df["in_q30"] == "Y", "d3_judgment_code"].value_counts().reindex(["A", "B", "C", "X"], fill_value=0)
st.bar_chart(d3_counts)

n_competing = int((df["competing_diagnosis_flag"] == "Y").sum())
st.metric(t("stats.metric_competing"), n_competing)

st.divider()
st.subheader(t("stats.by_clinic_header"))
by_clinic = df.groupby(["clinic_id", t("col.group")]).size().rename(t("stats.col_candidate_count")).reset_index()
st.bar_chart(by_clinic.set_index("clinic_id")[t("stats.col_candidate_count")])

st.divider()
st.subheader(t("stats.unconfirmed_header"))
st.table(pd.DataFrame([
    {t("stats.col_field"): t("stats.row_req02_field"), t("col.status"): t("stats.status_req02")},
    {t("stats.col_field"): t("stats.row_req03_field"), t("col.status"): t("stats.status_req03")},
    {t("stats.col_field"): "disease_code LIKE 'ZZZ%'",
     t("col.status"): t("stats.status_zzz", n=int((df["flag_zzz_pending_confirmation"] == "Y").sum()))},
    {t("stats.col_field"): "QC2 (C005-2)", t("col.status"): t("stats.status_qc2")},
    {t("stats.col_field"): "D4-1 P01-P11", t("col.status"): t("stats.status_d4")},
]), width="stretch")

st.divider()
st.subheader(t("stats.outcome_header"))
imported_review = st.session_state.get("imported_review_df")
imported_outcome = st.session_state.get("imported_outcome_df")
has_episode = imported_review is not None and (imported_review["episode_id"].astype(str).replace("NA", "") != "").any()
if imported_review is not None and imported_outcome is not None and has_episode:
    supp_df = build_supplementary_export(
        result.candidates, imported_review.to_dict("records"), imported_outcome.to_dict("records"),
    )
    rates = compute_outcome_rates(supp_df.to_dict("records"))

    def _pct(v):
        return "—" if v is None else f"{v:.1f}%"

    o1, o2 = st.columns(2)
    o1.metric(t("stats.outcome_denominator_t"), rates["denominator_t"])
    o2.metric(t("stats.outcome_held_back"), rates["held_back_count"])

    o3, o4, o5, o6 = st.columns(4)
    o3.metric(t("stats.outcome_composite_rate"), _pct(rates["composite_rate_percent"]))
    o4.metric(t("stats.outcome_fukaku_rate"), _pct(rates["fukaku_rate_percent"]))
    o5.metric(t("stats.outcome_admission_rate"), _pct(rates["admission_rate_percent"]))
    o6.metric(t("stats.outcome_transport_rate"), _pct(rates["transport_rate_percent"]))
    st.metric(t("stats.outcome_death_rate"), _pct(rates["death_rate_percent"]))

    st.caption(t("stats.outcome_caveat"))
else:
    st.info(t("stats.outcome_no_data"))

st.page_link("pages/3_Danh_sach_ung_vien.py", label=t("search.link_candidates"), icon="📋")
