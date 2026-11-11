"""Chi tiết 1 candidate (model v1.3.1)."""
import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent.parent
_ROOT_DIR = _APP_DIR.parent
for _p in (_APP_DIR, _ROOT_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import streamlit as st

from exports.review_template import build_review_csv_blank
from services.i18n import language_selector, t

st.set_page_config(page_title="Chi tiết ứng viên — AGRI CARE", layout="wide")
language_selector()

if "last_run_result" not in st.session_state:
    st.warning(t("common.no_run_warning"))
    st.page_link("pages/1_Tim_kiem.py", label=t("common.link_to_search"), icon="🔎")
    st.stop()

candidate_id = st.session_state.get("selected_candidate_id")
if not candidate_id:
    st.warning(t("detail.no_candidate_selected"))
    st.page_link("pages/3_Danh_sach_ung_vien.py", label=t("detail.link_back_to_list"), icon="📋")
    st.stop()

result = st.session_state.last_run_result
cand = next((c for c in result.candidates if c["candidate_id"] == candidate_id), None)
if cand is None:
    st.error(t("detail.candidate_not_found"))
    st.stop()

st.title(t("detail.title", id=candidate_id))

c1, c2, c3, c4 = st.columns(4)
c1.metric("Tháng đầu/cuối", f"{cand['first_record_month']} → {cand['last_record_month']}")
c2.metric("Số tháng liên tục", cand["record_months"])
c3.metric("Đường dùng (A13)", cand["route_class"])
c4.metric("ehr_source", cand["ehr_source"])

st.subheader("Thuốc kháng sinh tiêm/truyền (A11-A12)")
st.write(f"**Tên thuốc:** {cand['drug_names']}")
st.write(f"**Mã thuốc:** {cand['drug_codes']}")

st.divider()
st.subheader("病名 gắn vào candidate (A14-A16)")
st.caption("Mỗi病名 có 1 trạng thái D1 riêng (A=確定/活動性, S=疑い) — hiển thị tách biệt, không gộp.")
names = (cand["diagnosis_names"] or "").split("|")
codes = (cand["diagnosis_codes"] or "").split("|")
cats = (cand["diagnosis_categories"] or "").split("|")
if names and names[0]:
    for name, code, cat in zip(names, codes, cats):
        region, _, state = cat.partition(":")
        badge = "🟡 疑い" if state == "S" else "⚪ 確定/活動性"
        st.markdown(f"- **{name}** (`{code}`, 区分 {region}) — {badge}")
else:
    st.caption("Không có病名 nào được gắn trong khung thời gian của candidate này.")

st.divider()
st.subheader("Evidence reference (A17)")
st.code(cand["evidence_ref"], language=None)

st.session_state.setdefault("internal_progress_store", {})
progress = st.selectbox(
    t("detail.progress_label"),
    options=["Chưa rà soát", "Đang rà soát", "Đã xem"],
    index=["Chưa rà soát", "Đang rà soát", "Đã xem"].index(
        st.session_state.internal_progress_store.get(candidate_id, "Chưa rà soát")
    ),
)
st.session_state.internal_progress_store[candidate_id] = progress

imported_review = st.session_state.get("imported_review_df")
if imported_review is not None:
    rows = imported_review[imported_review["candidate_id"] == candidate_id]
    st.subheader("Dữ liệu review đã upload cho candidate này")
    if rows.empty:
        st.caption("Chưa có dòng review nào khớp candidate_id này trong file đã upload.")
    else:
        st.dataframe(rows, width="stretch", hide_index=True)

st.divider()
blank_review = build_review_csv_blank([cand])
st.download_button(
    "⬇ Tải file review (41 cột, A đã điền, B/C trống) cho candidate này",
    data=blank_review.to_csv(index=False).encode("utf-8-sig"),
    file_name=f"review_{candidate_id.replace(':', '_')}.csv", mime="text/csv",
)

st.page_link("pages/3_Danh_sach_ung_vien.py", label=t("detail.link_back_to_list"), icon="📋")
