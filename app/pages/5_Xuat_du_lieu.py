"""Block 7 -- Export."""
import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent.parent
_ROOT_DIR = _APP_DIR.parent
for _p in (_APP_DIR, _ROOT_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import streamlit as st

from exports.export_csv import (
    build_candidate_csv, build_disease_evidence_csv, build_medication_evidence_csv, build_procedure_evidence_csv,
)
from exports.review_template import build_outcome_template_blank, build_review_template_blank
from exports.supplementary_export import build_supplementary_export
from review_import import parse_outcome_csv, parse_review_csv
from services.i18n import language_selector, t

st.set_page_config(page_title="Xuất dữ liệu — AGRI CARE", layout="wide")
language_selector()
st.title(t("export.title"))

st.warning(t("export.draft_warning"))

if "last_run_result" not in st.session_state:
    st.warning(t("common.no_run_warning"))
    st.page_link("pages/1_Tim_kiem.py", label=t("common.link_to_search"), icon="🔎")
    st.stop()

result = st.session_state.last_run_result
run_id = result.run_meta.run_id

st.caption(t("export.run_caption", run_id=run_id, n=len(result.candidates)))

c1, c2, c3, c4 = st.columns(4)
with c1:
    df = build_candidate_csv(result)
    st.download_button("⬇ 03_candidate.csv", df.to_csv(index=False).encode("utf-8-sig"),
                        file_name=f"03_candidate_{run_id}.csv", mime="text/csv")
with c2:
    df = build_disease_evidence_csv(result)
    st.download_button("⬇ 04_disease_evidence.csv", df.to_csv(index=False).encode("utf-8-sig"),
                        file_name=f"04_disease_evidence_{run_id}.csv", mime="text/csv")
with c3:
    df = build_medication_evidence_csv(result)
    st.download_button("⬇ 05_medication_evidence.csv", df.to_csv(index=False).encode("utf-8-sig"),
                        file_name=f"05_medication_evidence_{run_id}.csv", mime="text/csv")
with c4:
    df = build_procedure_evidence_csv(result)
    st.download_button("⬇ 06_procedure_evidence.csv", df.to_csv(index=False).encode("utf-8-sig"),
                        file_name=f"06_procedure_evidence_{run_id}.csv", mime="text/csv")

st.divider()
st.subheader(t("export.blank_files_header"))
d1, d2 = st.columns(2)
with d1:
    blank_review = build_review_template_blank(result.candidates, run_id, result.run_meta.q_table_version, result.run_meta.dictionary_version)
    st.download_button(t("export.dl_review_template"), blank_review.to_csv(index=False).encode("utf-8-sig"),
                        file_name=f"07_manual_review_template_{run_id}.csv", mime="text/csv")
with d2:
    imported_review = st.session_state.get("imported_review_df")
    has_episode = imported_review is not None and (imported_review["episode_id"].astype(str).replace("NA", "") != "").any()
    if imported_review is not None and has_episode:
        blank_outcome = build_outcome_template_blank(imported_review.to_dict("records"))
        st.download_button(t("export.dl_outcome_template"), blank_outcome.to_csv(index=False).encode("utf-8-sig"),
                            file_name=f"08_outcome_template_{run_id}.csv", mime="text/csv")
    else:
        st.button(t("export.dl_outcome_template"), disabled=True, help=t("export.outcome_disabled_help"))

st.divider()
st.subheader(t("export.supp_header"))
st.warning(t("export.supp_warning"))
imported_review = st.session_state.get("imported_review_df")
imported_outcome = st.session_state.get("imported_outcome_df")
has_episode = imported_review is not None and (imported_review["episode_id"].astype(str).replace("NA", "") != "").any()
if imported_review is not None and imported_outcome is not None and has_episode:
    supp_df = build_supplementary_export(
        result.candidates, imported_review.to_dict("records"), imported_outcome.to_dict("records"),
    )
    st.download_button(t("export.dl_supplementary"), supp_df.to_csv(index=False).encode("utf-8-sig"),
                        file_name=f"12_supplementary_export_{run_id}.csv", mime="text/csv")
else:
    st.button(t("export.dl_supplementary"), disabled=True, help=t("export.supp_disabled_help"))

st.divider()
st.subheader(t("export.upload_header"))
f_review = st.file_uploader(t("candidates.upload_review_label"), type="csv", key="exp_up_review")
if f_review is not None:
    st.session_state.imported_review_df = parse_review_csv(f_review)
    st.success(t("export.loaded_generic_msg", n=len(st.session_state.imported_review_df)))
f_outcome = st.file_uploader(t("candidates.upload_outcome_label"), type="csv", key="exp_up_outcome")
if f_outcome is not None:
    st.session_state.imported_outcome_df = parse_outcome_csv(f_outcome)
    st.success(t("export.loaded_generic_msg", n=len(st.session_state.imported_outcome_df)))
