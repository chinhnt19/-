"""Trích xuất candidate (model v1.3.1: 1 trục注射用抗菌薬 AND 静注・点滴静注,
nhóm theo tháng liên tục -- xem rules/q_conditions.json)."""
import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent.parent
_ROOT_DIR = _APP_DIR.parent
for _p in (_APP_DIR, _ROOT_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import os

import streamlit as st

from _bootstrap import get_connection, get_clinic_master_cached, get_dictionaries, known_clinic_ids
from database.db_access import get_perform_month_bounds, load_disease_records, load_medical_records, get_fetched_at_range
from models.run_meta import RunMeta, new_run_id, today_str
from rules.clinic_tool_mapping import NAHT_CLINIC_IDS, clinic_group
from services.build_candidates import build_candidates
from services.i18n import language_selector, t

st.set_page_config(page_title="Tìm kiếm — AGRI CARE", layout="wide")
language_selector()

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

# ---------------------------------------------------------------------- Bộ lọc
st.sidebar.header(t("search.filter_header"))
group_label = clinics["clinic_id"].map(lambda c: clinic_group(c, known_clinic_ids()))
clinics_display = clinics.assign(group=group_label)
options = clinics_display.sort_values(["group", "clinic_id"])["clinic_id"].tolist()

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

if st.sidebar.button(t("search.reset_button")):
    st.rerun()

st.session_state.filters = {"clinic_ids": selected_clinics, "month_start": month_start, "month_end": month_end}

# ---------------------------------------------------------------------- Chạy
st.title(t("search.title"))
st.info(
    "Model v1.3.1: 1 candidate = 1 chuỗi tháng liên tục có算定注射用抗菌薬 (静注/点滴静注) cho "
    "1 bệnh nhân. Công cụ KHÔNG tự xác định treatment episode (quy tắc 14 ngày), Day 0, case_status "
    "hay転帰 — việc đó do reviewer làm trên file xuất ra (xem trang Xuất dữ liệu)."
)
st.warning(
    "Giới hạn dữ liệu đã biết (không phải lỗi, xem addendum v1.3.1 Mục 2.9/§6): A06 (tuổi) và A07 "
    "(giới tính) luôn để trống — DB không có trường nhân khẩu học nào. Bệnh danh gắn vào candidate "
    "chỉ lọc theo ngày bắt đầu, không lọc theo ngày転帰 (DB không có cột này)."
)

st.caption(
    f"Phiên bản dictionary: D1={dicts.d1.version} · D2={dicts.d2.version} · D3={dicts.d3.version} · "
    f"D4={dicts.d4.version} · D6={dicts.d6.version} (DRAFT)"
)

if st.button(t("search.run_button"), type="primary"):
    with st.spinner(t("search.spinner")):
        disease_df = load_disease_records(conn, selected_clinics, month_start, month_end)
        medical_df = load_medical_records(conn, selected_clinics, month_start, month_end)

        naht_scope = [c for c in selected_clinics if c in NAHT_CLINIC_IDS]
        homis_scope = [c for c in selected_clinics if c not in NAHT_CLINIC_IDS]
        naht_min, naht_max = get_fetched_at_range(conn, naht_scope)
        homis_min, homis_max = get_fetched_at_range(conn, homis_scope)

        run_meta = RunMeta(
            run_id=new_run_id(q_table_version="v1.3.1", dictionary_version=dicts.d1.version),
            run_date=today_str(),
            q_table_version="v1.3.1", dictionary_version=dicts.d1.version,
            db_fetched_at_naht=f"{naht_min}/{naht_max}" if naht_min else "NA",
            db_fetched_at_homis=f"{homis_min}/{homis_max}" if homis_min else "NA",
            search_period_start=month_start, search_period_end=month_end,
            lookback_start_date=month_start,
        )
        result = build_candidates(disease_df, medical_df, dicts, run_meta, known_clinic_ids())
        st.session_state.last_run_result = result
    st.success(
        f"Đã trích xuất {len(result.candidates)} candidate (run_id={run_meta.run_id}, "
        f"{len(disease_df):,} dòng病名, {len(medical_df):,} dòng thuốc đã đọc)."
    )

if "last_run_result" in st.session_state:
    r = st.session_state.last_run_result
    st.caption(f"Kết quả lần chạy gần nhất: run_id={r.run_meta.run_id}, {len(r.candidates)} candidate.")
    c1, c2 = st.columns(2)
    with c1:
        st.page_link("pages/2_Thong_ke.py", label=t("search.link_stats"), icon="📊")
    with c2:
        st.page_link("pages/3_Danh_sach_ung_vien.py", label=t("search.link_candidates"), icon="📋")
