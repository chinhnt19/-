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

st.subheader("Tổng quan")
c1, c2, c3 = st.columns(3)
c1.metric("Số candidate", len(df))
c2.metric("Số bệnh nhân (施設+患者番号)", df["patient_local_id"].nunique())
c3.metric("Số cơ sở", df["facility_id"].nunique())

st.divider()
st.subheader("Theo nhóm NAHT/HOMIS")
by_group = df.groupby(t("col.group")).size().rename("Số candidate")
st.bar_chart(by_group)

st.divider()
st.subheader("Theo đường dùng (A13 route_class)")
route_counts = df["route_class"].value_counts()
st.bar_chart(route_counts)
st.caption("皮下筋肉注射 (medical_class 31) không được tính là candidate, không xuất hiện ở đây.")

st.divider()
st.subheader("Độ dài candidate (số tháng liên tục có算定)")
st.bar_chart(df["record_months"].value_counts().sort_index())

st.divider()
st.subheader("Bệnh danh gắn vào candidate (A16 diagnosis_categories)")
st.caption(
    "Mỗi candidate có thể có nhiều病名, mỗi病名 có 1 trạng thái: A=確定（活動性）, S=疑い, "
    "theo D1_修飾語. 保留「呼吸器感染症の疑い」(B02) vẫn là quyết định của reviewer, không phải ở đây."
)
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
    cat_df = pd.DataFrame(sorted(cat_counter.items(), key=lambda kv: -kv[1]), columns=["区分", "số candidate"])
    st.dataframe(cat_df, hide_index=True, width="stretch")
    a_count, s_count = state_counter.get("A", 0), state_counter.get("S", 0)
    st.caption(f"⚪ 確定/活動性 (A): {a_count} lượt   ·   🟡 疑い (S): {s_count} lượt — luôn tách biệt, không gộp chung.")
else:
    st.caption("Không có病名 nào được gắn.")

st.divider()
st.subheader(t("stats.unconfirmed_header"))
st.table(pd.DataFrame([
    {"Hạng mục": "A06 age_at_start / A07 sex", "Trạng thái": "Luôn trống — DB không có trường nhân khẩu học"},
    {"Hạng mục": "病名 転帰日 (outcome date)", "Trạng thái": "DB không có cột này — chỉ lọc theo ngày bắt đầu"},
    {"Hạng mục": "D4 P08/P11 (入院中手技料/中心静脈注射)",
     "Trạng thái": "Chưa xác minh đầy đủ với medical_class thật — xem addendum Mục 5 #6"},
    {"Hạng mục": "disease_code LIKE 'ZZZ%'", "Trạng thái": "Chưa có ý nghĩa chính thức, chỉ đánh dấu"},
]), width="stretch")

st.divider()
st.subheader(t("stats.outcome_header"))
st.caption(
    "Quyết định tạm thời 2026-11-11: 保留 KHÔNG vào mẫu số chính, chỉ báo riêng. Nhập viện tính cả "
    "2 cách (toàn bộ / chỉ ngoài kế hoạch) vì công thức急変率 chính thức chưa chốt (addendum Mục 5 #1)."
)
imported = st.session_state.get("imported_review_df")
if imported is not None and (imported.get("case_status", pd.Series(dtype=str)) != "").any():
    rates = compute_outcome_rates(imported.to_dict("records"))

    def _pct(v):
        return "—" if v is None else f"{v:.1f}%"

    o1, o2, o3, o4 = st.columns(4)
    o1.metric("Mẫu số chính (対象, qua QC)", rates["denominator_t"])
    o2.metric("保留 (báo riêng)", rates["held_back_count"])
    o3.metric("対象外", rates["excluded_count"])
    o4.metric("対象 nhưng chưa qua QC", rates["qc_not_passed_count"])

    tab_all, tab_unplanned = st.tabs(["Định nghĩa 1: toàn bộ nhập viện", "Định nghĩa 2: chỉ ngoài kế hoạch"])
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
    st.caption(
        "割合はいずれもあり÷（あり＋なし）。確認不能の件数・割合は分子に含めない（CSV設計説明書v1.3.1 §8）。"
    )
else:
    st.info("Chưa có file review đã điền B/C được upload (trang Danh sách ứng viên / Xuất dữ liệu).")

st.page_link("pages/3_Danh_sach_ung_vien.py", label=t("search.link_candidates"), icon="📋")
