"""Xuất file CSV (model v1.3.1: 1 file thống nhất, 17 cột A + 22 cột B trống
+ 2 cột C trống = 41 cột) và kiểm tra V01-V09 trên file review đã upload."""
import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent.parent
_ROOT_DIR = _APP_DIR.parent
for _p in (_APP_DIR, _ROOT_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import pandas as pd
import streamlit as st

from exports.export_csv import build_candidate_csv, build_column_dictionary_csv
from exports.qc_checks import check_all
from exports.review_template import build_review_csv_blank
from review_import import parse_review_csv
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

if st.button(t("export.create_csv_button"), type="primary"):
    st.session_state.export_csv_cache = {
        "run_id": run_id,
        "df_a": build_candidate_csv(result),
        "df_full": build_review_csv_blank(result.candidates),
    }

cache = st.session_state.get("export_csv_cache")
if cache is None or cache["run_id"] != run_id:
    st.info(t("export.not_created_info"))
else:
    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            t("export.dl_candidate_v131_button"), cache["df_a"].to_csv(index=False).encode("utf-8-sig"),
            file_name=f"candidate_{run_id}.csv", mime="text/csv",
        )
    with c2:
        st.download_button(
            t("export.dl_review_v131_button"), cache["df_full"].to_csv(index=False).encode("utf-8-sig"),
            file_name=f"review_{run_id}.csv", mime="text/csv",
        )

st.caption(t("export.col_dict_caption"))
dict_df = build_column_dictionary_csv()
st.download_button(
    t("export.dl_col_dict_button"),
    dict_df.to_csv(index=False).encode("utf-8-sig"),
    file_name="column_dictionary.csv", mime="text/csv",
)

st.divider()
st.subheader(t("export.qc_upload_header"))
st.caption(t("export.qc_caption"))
f_review = st.file_uploader(t("candidates.upload_v131_label"), type="csv", key="exp_up_review")
if f_review is not None:
    st.session_state.imported_review_df = parse_review_csv(f_review)
    rows = st.session_state.imported_review_df.to_dict("records")
    st.success(t("export.loaded_generic_msg", n=len(rows)))

    findings_by_row = check_all(rows)
    if not findings_by_row:
        st.success(t("export.qc_no_issues"))
    else:
        n_error = sum(1 for fs in findings_by_row.values() for f in fs if f.severity == "エラー")
        n_warn = sum(1 for fs in findings_by_row.values() for f in fs if f.severity == "警告")
        st.warning(t("export.qc_issues_warning", n=len(findings_by_row), n_error=n_error, n_warn=n_warn))
        col_row, col_level, col_content = t("export.qc_col_row"), t("export.qc_col_level"), t("export.qc_col_content")
        out = []
        for i, fs in findings_by_row.items():
            for f in fs:
                out.append({
                    col_row: i + 2,  # +1 header, +1 0-index -> 1-index
                    "episode_id": rows[i].get("episode_id", ""),
                    "check": f.check_id, col_level: f.severity, col_content: f.message,
                })
        st.dataframe(pd.DataFrame(out), hide_index=True, width="stretch")
