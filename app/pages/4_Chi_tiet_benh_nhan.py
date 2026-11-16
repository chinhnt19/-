"""Chi tiết 1 candidate (model v1.3.1)."""
import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent.parent
_ROOT_DIR = _APP_DIR.parent
for _p in (_APP_DIR, _ROOT_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import streamlit as st

from _bootstrap import column_help_config
from exports.review_template import build_review_csv_blank
from services.column_glossary import describe as describe_column
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
c1.metric(
    t("detail.metric_month_range"), f"{cand['first_record_month']} → {cand['last_record_month']}",
    help=f"{describe_column('first_record_month')}\n\n{describe_column('last_record_month')}",
)
c2.metric(t("detail.metric_months_count"), cand["record_months"], help=describe_column("record_months"))
c3.metric(t("candidates.route_label"), cand["route_class"], help=describe_column("route_class"))
c4.metric("ehr_source", cand["ehr_source"], help=describe_column("ehr_source"))

st.subheader(t("detail.drug_v131_header"))
st.caption(f"{describe_column('drug_names')}\n\n{describe_column('drug_codes')}")
st.write(f"{t('detail.drug_name_label')} {cand['drug_names']}")
st.write(f"{t('detail.drug_code_label')} {cand['drug_codes']}")

st.divider()
st.subheader(t("detail.diagnosis_v131_header"))
st.caption(t("detail.diagnosis_state_caption"))
st.caption(
    f"{describe_column('diagnosis_names')}\n\n{describe_column('diagnosis_codes')}\n\n"
    f"{describe_column('diagnosis_categories')}"
)
names = (cand["diagnosis_names"] or "").split("|")
codes = (cand["diagnosis_codes"] or "").split("|")
cats = (cand["diagnosis_categories"] or "").split("|")
if names and names[0]:
    for name, code, cat in zip(names, codes, cats):
        region, _, state = cat.partition(":")
        badge = "🟡 疑い" if state == "S" else "⚪ 確定/活動性"
        st.markdown(f"- **{name}** (`{code}`, 区分 {region}) — {badge}")
else:
    st.caption(t("detail.no_diagnosis_v131_caption"))

st.divider()
st.subheader(t("detail.evidence_v131_header"))
st.caption(describe_column("evidence_ref"))
st.code(cand["evidence_ref"], language=None)

_PROGRESS_OPTIONS = ["not_reviewed", "in_review", "reviewed"]
_progress_labels = {
    "not_reviewed": t("detail.progress_not_reviewed"),
    "in_review": t("detail.progress_in_review"),
    "reviewed": t("detail.progress_reviewed"),
}
st.session_state.setdefault("internal_progress_store", {})
progress = st.selectbox(
    t("detail.progress_label"),
    options=_PROGRESS_OPTIONS,
    format_func=lambda k: _progress_labels[k],
    index=_PROGRESS_OPTIONS.index(
        st.session_state.internal_progress_store.get(candidate_id, "not_reviewed")
    ),
)
st.session_state.internal_progress_store[candidate_id] = progress

imported_review = st.session_state.get("imported_review_df")
if imported_review is not None:
    rows = imported_review[imported_review["candidate_id"] == candidate_id]
    st.subheader(t("detail.review_data_v131_header"))
    if rows.empty:
        st.caption(t("detail.no_review_match_caption"))
    else:
        st.dataframe(
            rows, width="stretch", hide_index=True,
            column_config=column_help_config(list(rows.columns)),
        )

st.divider()
blank_review = build_review_csv_blank([cand])
st.download_button(
    t("detail.download_review_v131_button"),
    data=blank_review.to_csv(index=False).encode("utf-8-sig"),
    file_name=f"review_{candidate_id.replace(':', '_')}.csv", mime="text/csv",
)

st.page_link("pages/3_Danh_sach_ung_vien.py", label=t("detail.link_back_to_list"), icon="📋")
