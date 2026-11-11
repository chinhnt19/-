"""Block 5 -- Candidate List."""
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
from review_import import parse_outcome_csv, parse_review_csv
from rules.clinic_tool_mapping import SMALL_FACILITY_PATIENT_THRESHOLD, clinic_group
from services.i18n import language_selector, t

st.set_page_config(page_title="Danh sách ứng viên — AGRI CARE", layout="wide")
language_selector()
st.title(t("candidates.title"))

if "last_run_result" not in st.session_state:
    st.warning(t("common.no_run_warning"))
    st.page_link("pages/1_Tim_kiem.py", label=t("common.link_to_search"), icon="🔎")
    st.stop()

result = st.session_state.last_run_result
df = pd.DataFrame(result.candidates)
if df.empty:
    st.info(t("candidates.no_candidates"))
    st.stop()

st.session_state.setdefault("internal_progress_store", {})

df[t("col.group")] = df["clinic_id"].map(lambda c: clinic_group(c, known_clinic_ids()))
patient_counts = df.groupby("clinic_id")["candidate_id"].count()
small_clinics = [c for c, n in patient_counts.items() if n < SMALL_FACILITY_PATIENT_THRESHOLD]
if len(df["clinic_id"].unique()) == 1 and df["clinic_id"].iloc[0] in small_clinics:
    st.warning(t("candidates.small_clinic_warning", n=patient_counts.iloc[0]))

st.subheader(t("candidates.upload_header"))
col_u1, col_u2 = st.columns(2)
with col_u1:
    f_review = st.file_uploader(t("candidates.upload_review_label"), type="csv", key="up_review")
    if f_review is not None:
        st.session_state.imported_review_df = parse_review_csv(f_review)
        st.success(t("candidates.loaded_review_msg", n=len(st.session_state.imported_review_df)))
with col_u2:
    f_outcome = st.file_uploader(t("candidates.upload_outcome_label"), type="csv", key="up_outcome")
    if f_outcome is not None:
        st.session_state.imported_outcome_df = parse_outcome_csv(f_outcome)
        st.success(t("candidates.loaded_outcome_msg", n=len(st.session_state.imported_outcome_df)))

st.divider()
st.subheader(t("candidates.quick_filter_header"))
f1, f2, f3 = st.columns(3)
cells = f1.multiselect(t("candidates.filter_source_label"), sorted(df["combination_cell"].unique()))
d3_codes = f2.multiselect("D3", sorted(df["d3_judgment_code"].unique()))
groups = f3.multiselect(t("col.group"), sorted(df[t("col.group")].unique()))

view = df.copy()
if cells:
    view = view[view["combination_cell"].isin(cells)]
if d3_codes:
    view = view[view["d3_judgment_code"].isin(d3_codes)]
if groups:
    view = view[view[t("col.group")].isin(groups)]

st.caption(t("candidates.filtered_caption", shown=len(view), total=len(df)))

view = view.copy()
view[t("candidates.col_evidence")] = (
    view["n_disease_evidence_rows"].astype(str) + "D/" +
    view["n_medication_evidence_rows"].astype(str) + "M/" +
    view["n_procedure_evidence_rows"].astype(str) + "P"
)
view["Q31/Q32"] = view.apply(lambda r: ("⚑Q31 " if r["in_q31"] == "Y" else "") + ("⚑Q32" if r["in_q32"] == "Y" else ""), axis=1)

display_cols = [
    "candidate_id", t("col.group"), "combination_cell", "Q31/Q32", "d3_judgment_code",
    "competing_diagnosis_flag", "needs_form_check", "in_set_c_narrow_qc2",
    "flag_zzz_pending_confirmation", t("candidates.col_evidence"),
]
st.dataframe(view[display_cols], width="stretch", hide_index=True, height=420)

st.divider()
st.subheader(t("candidates.detail_header"))
pick = st.selectbox("candidate_id", options=view["candidate_id"].tolist())
if st.button(t("candidates.open_detail_button")):
    st.session_state.selected_candidate_id = pick
    st.switch_page("pages/4_Chi_tiet_benh_nhan.py")

st.page_link("pages/5_Xuat_du_lieu.py", label=t("candidates.link_export"), icon="⬇️")
