"""Block 2 (sidebar filters) + Block 3 (Cohort Search)."""
import os
import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent.parent
_ROOT_DIR = _APP_DIR.parent
for _p in (_APP_DIR, _ROOT_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import streamlit as st

from _bootstrap import get_connection, get_clinic_master_cached, get_dictionaries, known_clinic_ids
from database.db_access import get_perform_month_bounds, load_disease_records, load_medical_points, load_medical_records
from models.run_meta import RunMeta, new_run_id, today_str
from rules.clinic_tool_mapping import NAHT_CLINIC_IDS, clinic_group
from rules.q_conditions import EXCLUSION_GRANULARITY_MONTH, EXCLUSION_GRANULARITY_PATIENT
from services.aggregate import run_pipeline
from database.db_access import get_fetched_at_range
from services.i18n import language_selector, t

st.set_page_config(page_title="Tìm kiếm — AGRI CARE", layout="wide")
language_selector()

# Widen the sidebar so facility names have more room before the multiselect
# pill truncates with "..." -- Streamlit's default sidebar width (~21rem) is
# too narrow for "[NAHT] アグリホームクリニック ひたち (clinic_hitachi)"-style
# labels. Scoped to this page only (where the facility filter lives).
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] { min-width: 26rem; max-width: 34rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

conn = get_connection()
clinics = get_clinic_master_cached()
dicts = get_dictionaries()

# ---------------------------------------------------------------------- Block 2
st.sidebar.header(t("search.filter_header"))
group_label = clinics["clinic_id"].map(lambda c: clinic_group(c, known_clinic_ids()))
clinics_display = clinics.assign(group=group_label)
options = clinics_display.sort_values(["group", "clinic_id"])["clinic_id"].tolist()

# Every clinic_name in this DB shares one common prefix ("アグリホームクリニック ")
# -- computed here, not hardcoded, so it still works if a future clinic
# doesn't share it. Stripping it means the part that actually distinguishes
# one facility from another appears FIRST in the pill label, right after the
# [NAHT]/[HOMIS] badge -- so even when the pill truncates, the user still
# sees the distinguishing text instead of just the redundant shared prefix
# (which is what was happening before: every pill read "[NAHT] アグリホーム...").
_all_names = clinics["clinic_name"].tolist()
_common_prefix = os.path.commonprefix(_all_names).rstrip()
_name_by_id = clinics.set_index("clinic_id")["clinic_name"]


def _short_name(cid: str) -> str:
    name = _name_by_id.get(cid, cid)
    if _common_prefix and name.startswith(_common_prefix):
        short = name[len(_common_prefix):].strip()
        return short or name
    return name


def _fmt_clinic(cid: str) -> str:
    grp = clinic_group(cid, known_clinic_ids())
    return f"[{grp}] {_short_name(cid)} ({cid})"


selected_clinics = st.sidebar.multiselect(
    t("search.facility_label"), options=options, default=options, format_func=_fmt_clinic,
    help=t("search.facility_help", prefix=_common_prefix),
)

month_min, month_max = get_perform_month_bounds(conn)
st.sidebar.caption(t("search.month_range_caption", min=month_min, max=month_max))
month_start = st.sidebar.text_input(t("search.month_start_label"), value=month_min or "")
month_end = st.sidebar.text_input(t("search.month_end_label"), value=month_max or "")

exclusion_granularity = st.sidebar.radio(
    t("search.exclusion_radio_label"),
    options=[EXCLUSION_GRANULARITY_PATIENT, EXCLUSION_GRANULARITY_MONTH],
    format_func=lambda v: t("search.exclusion_opt_patient") if v == EXCLUSION_GRANULARITY_PATIENT else t("search.exclusion_opt_month"),
)
if exclusion_granularity == EXCLUSION_GRANULARITY_MONTH:
    st.sidebar.warning(t("search.exclusion_month_warning"))

if st.sidebar.button(t("search.reset_button")):
    st.rerun()

st.session_state.filters = {
    "clinic_ids": selected_clinics, "month_start": month_start, "month_end": month_end,
    "exclusion_granularity": exclusion_granularity,
}

# ---------------------------------------------------------------------- Block 3
st.title(t("search.title"))
st.info(t("search.info_full_dict"))

b1, b2 = st.columns(2)
with b1:
    st.warning(t("search.warn_qc_not_official"))
with b2:
    st.warning(t("search.warn_qc2_unverified"))

st.caption(t("search.dict_version_caption", d1=dicts.d1.version, d2=dicts.d2.version, d3=dicts.d3.version, d4=dicts.d4.version))

if st.button(t("search.run_button"), type="primary"):
    with st.spinner(t("search.spinner")):
        disease_df = load_disease_records(conn, selected_clinics, month_start, month_end)
        medical_df = load_medical_records(conn, selected_clinics, month_start, month_end)
        points_df = load_medical_points(conn, selected_clinics, month_start, month_end)

        naht_scope = [c for c in selected_clinics if c in NAHT_CLINIC_IDS]
        homis_scope = [c for c in selected_clinics if c not in NAHT_CLINIC_IDS]
        naht_min, naht_max = get_fetched_at_range(conn, naht_scope)
        homis_min, homis_max = get_fetched_at_range(conn, homis_scope)

        run_meta = RunMeta(
            run_id=new_run_id(q_table_version="v1.0", dictionary_version=dicts.d1.version),
            run_date=today_str(),
            q_table_version="v1.0", dictionary_version=dicts.d1.version,
            db_fetched_at_naht=f"{naht_min}/{naht_max}" if naht_min else "NA",
            db_fetched_at_homis=f"{homis_min}/{homis_max}" if homis_min else "NA",
            search_period_start=month_start, search_period_end=month_end,
            lookback_start_date=month_start, exclusion_granularity=exclusion_granularity,
        )
        result = run_pipeline(disease_df, medical_df, points_df, dicts, run_meta, known_clinic_ids())
        st.session_state.last_run_result = result
    st.success(t(
        "search.success_msg", run_id=run_meta.run_id, n_candidates=len(result.candidates),
        n_disease=f"{len(disease_df):,}", n_medical=f"{len(medical_df):,}",
    ))

if "last_run_result" in st.session_state:
    r = st.session_state.last_run_result
    st.caption(t("search.last_result_caption", run_id=r.run_meta.run_id, n_candidates=len(r.candidates)))
    c1, c2 = st.columns(2)
    with c1:
        st.page_link("pages/2_Thong_ke.py", label=t("search.link_stats"), icon="📊")
    with c2:
        st.page_link("pages/3_Danh_sach_ung_vien.py", label=t("search.link_candidates"), icon="📋")
