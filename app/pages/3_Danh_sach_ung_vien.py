"""Danh sách candidate (model v1.3.1) + upload file review đã điền."""
import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent.parent
_ROOT_DIR = _APP_DIR.parent
for _p in (_APP_DIR, _ROOT_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import pandas as pd
import streamlit as st

from _bootstrap import column_help_config, known_clinic_ids
from review_import import parse_review_csv
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

df[t("col.group")] = df["facility_id"].map(lambda c: clinic_group(c, known_clinic_ids()))
patient_counts = df.groupby("facility_id")["patient_local_id"].nunique()
small_clinics = [c for c, n in patient_counts.items() if n < SMALL_FACILITY_PATIENT_THRESHOLD]
if len(df["facility_id"].unique()) == 1 and df["facility_id"].iloc[0] in small_clinics:
    st.warning(t("candidates.small_clinic_warning", n=patient_counts.iloc[0]))

st.subheader(t("candidates.upload_v131_header"))
st.caption(t("candidates.upload_v131_caption"))
f_review = st.file_uploader(t("candidates.upload_v131_label"), type="csv", key="up_review")
if f_review is not None:
    st.session_state.imported_review_df = parse_review_csv(f_review)
    st.success(t("export.loaded_generic_msg", n=len(st.session_state.imported_review_df)))

st.divider()
st.subheader(t("candidates.quick_filter_header"))
f1, f2, f3 = st.columns(3)
groups = f1.multiselect(t("col.group"), sorted(df[t("col.group")].unique()))
routes = f2.multiselect(t("candidates.route_label"), sorted(set(
    tok for r in df["route_class"] for tok in (r or "").split("|") if tok
)))
has_suspect = f3.checkbox(t("candidates.suspect_checkbox"))

view = df.copy()
if groups:
    view = view[view[t("col.group")].isin(groups)]
if routes:
    view = view[view["route_class"].apply(lambda r: any(tok in (r or "").split("|") for tok in routes))]
if has_suspect:
    view = view[view["diagnosis_categories"].str.contains(":S")]

st.caption(t("candidates.filtered_caption", shown=len(view), total=len(df)))

display_cols = [
    "candidate_id", t("col.group"), "first_record_month", "last_record_month", "record_months",
    "route_class", "drug_names", "diagnosis_names",
]
st.dataframe(
    view[display_cols], width="stretch", hide_index=True, height=420,
    column_config=column_help_config(display_cols),
)

st.divider()
st.subheader(t("candidates.detail_header"))
pick = st.selectbox("candidate_id", options=view["candidate_id"].tolist())
if st.button(t("candidates.open_detail_button")):
    st.session_state.selected_candidate_id = pick
    st.switch_page("pages/4_Chi_tiet_benh_nhan.py")

st.page_link("pages/5_Xuat_du_lieu.py", label=t("candidates.link_export"), icon="⬇️")
