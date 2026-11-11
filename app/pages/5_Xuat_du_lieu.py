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

from exports.export_csv import build_candidate_csv
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

c1, c2 = st.columns(2)
with c1:
    df_a = build_candidate_csv(result)
    st.download_button(
        "⬇ Candidate (17 cột A, chỉ tool)", df_a.to_csv(index=False).encode("utf-8-sig"),
        file_name=f"candidate_{run_id}.csv", mime="text/csv",
    )
with c2:
    df_full = build_review_csv_blank(result.candidates)
    st.download_button(
        "⬇ File review (41 cột, A đã điền + B/C trống)", df_full.to_csv(index=False).encode("utf-8-sig"),
        file_name=f"review_{run_id}.csv", mime="text/csv",
    )

st.divider()
st.subheader("Upload file review đã điền để kiểm tra (V01-V09)")
st.caption(
    "Điểm kiểm tra chỉ tìm lỗi nhập liệu (CSV設計説明書v1.3.1 §7) — không đánh giá case_status/Day0/"
    "転帰 có ĐÚNG hay không, chỉ xem có NHẤT QUÁN hay không. Người二次確認 (C01/C02) vẫn là người quyết."
)
f_review = st.file_uploader("File review (CSV, 41 cột)", type="csv", key="exp_up_review")
if f_review is not None:
    st.session_state.imported_review_df = parse_review_csv(f_review)
    rows = st.session_state.imported_review_df.to_dict("records")
    st.success(f"Đã nạp {len(rows)} dòng.")

    findings_by_row = check_all(rows)
    if not findings_by_row:
        st.success("Không phát hiện vấn đề nào qua V01-V09.")
    else:
        n_error = sum(1 for fs in findings_by_row.values() for f in fs if f.severity == "エラー")
        n_warn = sum(1 for fs in findings_by_row.values() for f in fs if f.severity == "警告")
        st.warning(f"{len(findings_by_row)} dòng có vấn đề — {n_error} lỗi (エラー), {n_warn} cảnh báo (警告).")
        out = []
        for i, fs in findings_by_row.items():
            for f in fs:
                out.append({
                    "dòng": i + 2,  # +1 header, +1 0-index -> 1-index
                    "episode_id": rows[i].get("episode_id", ""),
                    "check": f.check_id, "mức": f.severity, "nội dung": f.message,
                })
        st.dataframe(pd.DataFrame(out), hide_index=True, width="stretch")
