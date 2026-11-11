"""Block 6 -- Patient (Candidate) Detail."""
import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent.parent
_ROOT_DIR = _APP_DIR.parent
for _p in (_APP_DIR, _ROOT_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import pandas as pd
import streamlit as st

from exports.export_csv import build_disease_evidence_csv, build_medication_evidence_csv, build_procedure_evidence_csv
from exports.review_template import build_review_template_blank
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
c1.metric(t("detail.metric_combination_cell"), cand["combination_cell"])
c2.metric("D3", cand["d3_judgment_code"])
c3.metric(t("detail.metric_competing"), cand["competing_diagnosis_flag"])
c4.metric("QC2 (C005-2)", cand["in_set_c_narrow_qc2"])

st.session_state.setdefault("internal_progress_store", {})
# Các giá trị tuỳ chọn ("Chưa rà soát"...) được dùng làm GIÁ TRỊ NỘI BỘ lưu
# trong session_state (so sánh qua .index()) -- cố tình KHÔNG dịch qua t()
# để không phá vỡ việc so khớp khi người dùng đổi ngôn ngữ giữa phiên.
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
    st.subheader(t("detail.review_record_header"))
    if rows.empty:
        st.caption(t("detail.no_review_row_caption"))
    else:
        st.dataframe(rows, width="stretch", hide_index=True)
        imported_outcome = st.session_state.get("imported_outcome_df")
        if imported_outcome is not None:
            ep_ids = [e for e in rows["episode_id"].unique() if e and e != "NA"]
            out_rows = imported_outcome[imported_outcome["episode_id"].isin(ep_ids)]
            if not out_rows.empty:
                st.dataframe(out_rows, width="stretch", hide_index=True)

st.divider()
disease_df = build_disease_evidence_csv(result, {candidate_id})
medication_df = build_medication_evidence_csv(result, {candidate_id})
procedure_df = build_procedure_evidence_csv(result, {candidate_id})

st.subheader(t("detail.disease_evidence_header", n=len(disease_df)))
if disease_df.empty:
    st.caption(t("detail.no_rows_caption"))
else:
    def _hl(row):
        return ["background-color: #fff3cd" if row["flag_zzz_pending_confirmation"] == "Y" else "" for _ in row]
    st.dataframe(disease_df.style.apply(_hl, axis=1), width="stretch")

st.subheader(t("detail.medication_evidence_header", n=len(medication_df)))
st.caption(t("detail.medication_ehr_caption"))
if medication_df.empty:
    st.caption(t("detail.no_rows_caption"))
else:
    st.dataframe(medication_df, width="stretch")

st.subheader(t("detail.procedure_evidence_header", n=len(procedure_df)))
if procedure_df.empty:
    st.caption(t("detail.no_procedure_rows_caption"))
else:
    st.dataframe(procedure_df, width="stretch")

if cand["in_q30"] == "Y":
    st.subheader(t("detail.q40_header", n=cand["q40_hint_count"]))
    hints = medication_df[medication_df["matched_q40_hint"] == "Y"]
    if hints.empty:
        st.caption(t("detail.no_hit_caption"))
    else:
        st.dataframe(hints[["perform_month", "medication_name_original", "q40_hint_matched_text"]], width="stretch", hide_index=True)
    st.caption(t("detail.q40_disclaimer"))

st.divider()
col_a, col_b = st.columns(2)
with col_a:
    combined = pd.concat([
        disease_df.assign(_sheet="disease"), medication_df.assign(_sheet="medication"), procedure_df.assign(_sheet="procedure"),
    ], ignore_index=True) if not (disease_df.empty and medication_df.empty and procedure_df.empty) else pd.DataFrame()
    st.download_button(
        t("detail.download_evidence_label"),
        data=combined.to_csv(index=False).encode("utf-8-sig"), file_name=f"evidence_{candidate_id.replace(':', '_')}.csv",
        mime="text/csv", disabled=combined.empty,
    )
with col_b:
    blank_review = build_review_template_blank([cand], result.run_meta.run_id, result.run_meta.q_table_version, result.run_meta.dictionary_version)
    st.download_button(
        t("detail.download_review_label"),
        data=blank_review.to_csv(index=False).encode("utf-8-sig"),
        file_name=f"review_template_{candidate_id.replace(':', '_')}.csv", mime="text/csv",
    )

st.page_link("pages/3_Danh_sach_ung_vien.py", label=t("detail.link_back_to_list"), icon="📋")
