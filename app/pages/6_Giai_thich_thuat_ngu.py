"""Trang tra cứu: giải thích các mã/nhóm/trạng thái trong từ điển D1-D4, kèm
tab "Giới thiệu" tổng quan công cụ (bản rút gọn của báo cáo công khai cho
người dùng không chuyên kỹ thuật).

Tab "Giới thiệu" đọc database (chỉ đọc) để tính số dòng/kiểm tra cơ sở chưa
được ánh xạ trực tiếp từ dữ liệu thật, luôn cập nhật -- các tab D1-D4/Nghi
vấn còn lại không đọc database, không ảnh hưởng pipeline tìm kiếm/tổng hợp
ứng viên ở các trang khác.
"""
import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent.parent
_ROOT_DIR = _APP_DIR.parent
for _p in (_APP_DIR, _ROOT_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import pandas as pd
import streamlit as st

from _bootstrap import get_connection, get_dictionaries
from database.db_access import get_table_row_counts, get_unmapped_clinic_summary
from services.glossary import read_csv_rows
from services.i18n import get_lang, language_selector, t
from services.open_questions import QUESTIONS, SECTIONS, STATUS_PROPOSED, STATUS_RESOLVED, STATUS_UNVERIFIED

st.set_page_config(page_title="Giải thích thuật ngữ — AGRI CARE", layout="wide")
language_selector()

st.title(t("glossary.title"))
st.caption(t("glossary.caption"))

conn = get_connection()
dicts = get_dictionaries()

# --------------------------------------------------------------- Tổng quan pipeline
st.subheader(t("glossary.overview_header"))
flow = st.columns([2, 1, 2, 1, 2, 1, 2])
flow[0].markdown(f"**D1**\n\n{t('glossary.overview_flow_d1')}")
flow[1].markdown("### →")
flow[2].markdown(f"**D2**\n\n{t('glossary.overview_flow_d2')}")
flow[3].markdown("### →")
flow[4].markdown(f"**Q30**\n\n{t('glossary.overview_flow_q30')}")
flow[5].markdown("### →")
flow[6].markdown(f"**D3**\n\n{t('glossary.overview_flow_d3')}")
st.caption(t("glossary.overview_flow_d4_note"))

for key in (
    "glossary.overview_d1", "glossary.overview_d2", "glossary.overview_merge",
    "glossary.overview_d3", "glossary.overview_d4",
):
    st.markdown(t(key))

st.caption(t("glossary.overview_source"))
st.divider()

tab_intro, tab_how, tab_d1, tab_d2, tab_d3, tab_d4, tab_oq = st.tabs([
    t("glossary.tab_intro"), t("glossary.tab_howitworks"),
    t("glossary.tab_d1"), t("glossary.tab_d2"), t("glossary.tab_d3"), t("glossary.tab_d4"),
    t("glossary.tab_open_questions"),
])

# --------------------------------------------------------------------- Giới thiệu
with tab_intro:
    st.subheader(t("intro.quick_answer_title"))
    st.success(t("intro.quick_answer_body"))
    st.warning(t("intro.caveat_no_signoff"))

    unmapped = get_unmapped_clinic_summary(conn)
    if not unmapped.empty:
        st.error(t("intro.orphan_title"))
        st.caption(t("intro.orphan_body"))
        display_df = unmapped.rename(columns={
            "clinic_id": t("col.id"),
            "n_disease_rows": t("intro.orphan_col_disease"),
            "n_medical_rows": t("intro.orphan_col_medical"),
            "n_points_rows": t("intro.orphan_col_points"),
        })
        st.dataframe(display_df, hide_index=True, width="stretch")
        totals = unmapped[["n_disease_rows", "n_medical_rows", "n_points_rows"]].sum()
        st.caption(t(
            "intro.orphan_total",
            disease=f"{totals['n_disease_rows']:,}",
            medical=f"{totals['n_medical_rows']:,}",
            points=f"{totals['n_points_rows']:,}",
        ))
    else:
        st.success(t("intro.orphan_resolved"))

    st.divider()
    col_can, col_cannot = st.columns(2)
    with col_can:
        st.markdown(f"**{t('intro.can_title')}**")
        st.markdown(t("intro.can_body"))
    with col_cannot:
        st.markdown(f"**{t('intro.cannot_title')}**")
        st.markdown(t("intro.cannot_body"))

    st.divider()
    st.subheader(t("intro.db_header"))
    counts = get_table_row_counts(conn)
    d1c, d2c, d3c, d4c = st.columns(4)
    d1c.metric("clinic_master", f"{counts['clinic_master']:,}", help=t("intro.db_clinic_master"))
    d2c.metric("disease_records", f"{counts['disease_records']:,}", help=t("intro.db_disease_records"))
    d3c.metric("medical_records", f"{counts['medical_records']:,}", help=t("intro.db_medical_records"))
    d4c.metric("medical_points", f"{counts['medical_points']:,}", help=t("intro.db_medical_points"))
    st.caption(t("intro.db_caption"))

    st.markdown(f"**{t('intro.diagram_header')}**")
    st.caption(t("intro.diagram_caption"))
    hub = st.columns([1, 2, 1])
    hub[1].markdown(f"<div style='text-align:center; border:1px solid #888; border-radius:8px; padding:8px'>"
                     f"🏥 <b>clinic_master</b><br><small>{t('intro.db_clinic_master')}</small></div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center; color:#888'>↓ clinic_id ↓</div>", unsafe_allow_html=True)
    spokes = st.columns(3)
    spoke_defs = [
        ("disease_records", t("intro.db_disease_records")),
        ("medical_records", t("intro.db_medical_records")),
        ("medical_points", t("intro.db_medical_points")),
    ]
    for col, (name, desc) in zip(spokes, spoke_defs):
        col.markdown(f"<div style='text-align:center; border:1px solid #888; border-radius:8px; padding:8px'>"
                      f"<b>{name}</b><br><small>{desc}</small></div>", unsafe_allow_html=True)
    st.caption(t("intro.diagram_note"))

    st.divider()
    st.subheader(t("intro.run_header"))
    for key in ("intro.run_1", "intro.run_2", "intro.run_3", "intro.run_4", "intro.run_5", "intro.run_6"):
        st.markdown(f"- {t(key)}")

    st.divider()
    st.info(t("intro.approval_status"))
    st.caption(t("intro.pointer"))

# ------------------------------------------------------------- Cách hoạt động
with tab_how:
    st.caption(t("how.caption"))

    st.subheader(t("how.sets_header"))
    st.markdown(t("how.sets_intro"))
    sa, sb, sc = st.columns(3)
    sa.markdown(t("how.set_a"))
    sb.markdown(t("how.set_b"))
    sc.markdown(t("how.set_c"))

    _VENN_SVG = """
    <svg viewBox="0 0 460 300" style="max-width:420px; width:100%; display:block; margin:0.6rem auto;"
         role="img" aria-label="So do Venn 3 tap hop A, B, C">
      <circle cx="175" cy="130" r="100" fill="none" stroke="#2e8b6f" stroke-width="2"/>
      <circle cx="255" cy="130" r="100" fill="none" stroke="#888" stroke-width="1.6"/>
      <circle cx="215" cy="205" r="100" fill="none" stroke="#888" stroke-width="1.6" opacity="0.8"/>
      <text x="90" y="75" font-size="13" font-weight="700" fill="#2e8b6f">A</text>
      <text x="315" y="75" font-size="13" font-weight="600" fill="currentColor">B</text>
      <text x="215" y="285" font-size="13" font-weight="600" fill="currentColor" text-anchor="middle">C</text>
      <text x="215" y="110" font-size="13" font-weight="700" fill="#2e8b6f" text-anchor="middle">A+B</text>
      <text x="130" y="130" font-size="11" fill="currentColor" text-anchor="middle" opacity="0.8">chỉ A</text>
      <text x="300" y="130" font-size="11" fill="currentColor" text-anchor="middle" opacity="0.8">chỉ B</text>
      <text x="215" y="235" font-size="11" fill="currentColor" text-anchor="middle" opacity="0.8">chỉ C</text>
    </svg>
    """
    st.markdown(_VENN_SVG, unsafe_allow_html=True)
    st.info(t("how.sets_note"))

    st.divider()
    st.subheader(t("how.certainty_header"))
    st.markdown(t("how.certainty_intro"))
    ca, cs, ch, cx = st.columns(4)
    ca.success(t("how.certainty_a"))
    cs.success(t("how.certainty_s"))
    ch.error(t("how.certainty_h"))
    cx.error(t("how.certainty_x"))

    st.divider()
    st.subheader(t("how.undecided_header"))
    st.warning(t("how.undecided_body"))

    st.divider()
    st.subheader(t("how.d5_header"))
    st.markdown(t("how.d5_body"))
    try:
        d5_rows = [r for r in read_csv_rows("D5_context_flags.csv") if r["row_type"] == "CONTEXT_FLAG"]
        d5_df = pd.DataFrame([
            {
                t("col.code"): r["name_or_code"],
                t("col.description"): r["description"],
                t("col.source"): r["source_ref"],
            }
            for r in d5_rows
        ])
        st.dataframe(d5_df, hide_index=True, width="stretch")
        if d5_rows:
            st.caption(f"D5 version: {d5_rows[0]['version']}")
    except FileNotFoundError:
        st.caption("dictionaries/D5_context_flags.csv chưa có trong lần chạy này.")

    st.divider()
    st.subheader(t("how.patterns_header"))
    st.markdown(t("how.patterns_body"))

    st.divider()
    st.subheader(t("how.refs_header"))
    for key in ("how.ref_master", "how.ref_policy", "how.ref_pharma", "how.ref_csvguide", "how.ref_patterns", "how.ref_dbprofile"):
        st.markdown(f"- {t(key)}")

# --------------------------------------------------------------------------- D1
with tab_d1:
    _d1_rows = read_csv_rows("D1_disease.csv")

    st.subheader(t("glossary.d1_categories_header"))
    st.caption(t("glossary.d1_categories_caption"))
    cat_rows = sorted(
        (r for r in _d1_rows if r["row_type"] == "CATEGORY"),
        key=lambda r: int(r["order"]),
    )
    cat_df = pd.DataFrame([
        {
            t("col.order"): r["order"],
            t("col.code"): r["d1_category"],
            t("col.name_jp"): r["category_name_jp"],
            t("col.pattern"): r["pattern_or_term"],
            t("col.source"): r["source_ref"],
        }
        for r in cat_rows
    ])
    st.dataframe(cat_df, hide_index=True, width="stretch")

    st.divider()
    st.subheader(t("glossary.d1_modifiers_header"))
    st.caption(t("glossary.d1_modifiers_caption"))
    mod_rows = [r for r in _d1_rows if r["row_type"] == "MODIFIER"]
    mod_df = pd.DataFrame([
        {
            t("col.id"): r["id"],
            t("col.pattern"): r["pattern_or_term"],
            t("col.status"): r["status"],
            t("col.disposition"): r["main_analysis_disposition_jp"],
            t("col.source"): r["source_ref"],
        }
        for r in mod_rows
    ])
    st.dataframe(mod_df, hide_index=True, width="stretch")
    st.caption(t("glossary.d1_status_legend"))

# --------------------------------------------------------------------------- D2
with tab_d2:
    st.subheader(t("glossary.d2_header"))
    st.caption(t("glossary.d2_caption"))
    d2_rows = [r for r in read_csv_rows("D2_antibiotic.csv") if r["row_type"] == "SEARCH_TERM"]
    d2_df = pd.DataFrame([
        {
            t("col.id"): r["ingredient_id"],
            t("col.name_jp"): r["ingredient_name_jp"],
            t("col.search_term"): r["search_term"],
            t("col.group"): r["group"],
            t("col.confirmed"): r["confirmed_status"],
            t("col.form_check"): ("要" if "要剤形確認" in r["search_term_type"] else ""),
            # D2 không có cột source_ref riêng (chỉ source_table) -- Master Document
            # không ghi rõ số §-mục cho D2-1/D2-2/D2-3, khác với D1/D3/D4 (xem
            # dictionary_specification.md §5). Không tự suy diễn số mục.
            t("col.source"): f"Master Doc v1.0, Bảng {r['source_table']} (chưa ghi rõ §-mục trong tài liệu nguồn)",
        }
        for r in d2_rows
    ])
    st.dataframe(d2_df, hide_index=True, width="stretch")
    n_confirmed = sum(1 for r in d2_rows if r["confirmed_status"] == "確認済")
    st.caption(t("glossary.d2_footer", confirmed=n_confirmed, total=len(d2_rows)))

# --------------------------------------------------------------------------- D3
with tab_d3:
    d3_rows = read_csv_rows("D3_judgment.csv")

    st.subheader(t("glossary.d3_groups_header"))
    group_df = pd.DataFrame([
        {
            t("col.group"): r["key1"],
            t("col.description"): r["value_or_code"],
            t("col.members"): r["description"],
            t("col.source"): r["source_ref"],
        }
        for r in d3_rows if r["row_type"] == "ANTIBIOTIC_GROUP"
    ])
    st.dataframe(group_df, hide_index=True, width="stretch")

    st.divider()
    st.subheader(t("glossary.d3_judgment_header"))
    jc_df = pd.DataFrame([
        {
            t("col.code"): r["key1"],
            t("col.name_jp"): r["value_or_code"],
            t("col.description"): r["description"],
            t("col.source"): r["source_ref"],
        }
        for r in d3_rows if r["row_type"] == "JUDGMENT_CODE"
    ])
    st.dataframe(jc_df, hide_index=True, width="stretch")

    st.divider()
    st.subheader(t("glossary.d3_matrix_header"))
    st.caption(t("glossary.d3_matrix_caption"))
    matrix_cells = [r for r in d3_rows if r["row_type"] == "MATRIX_CELL"]
    matrix_df = pd.DataFrame(matrix_cells)[["key1", "key2", "value_or_code"]]
    pivot = matrix_df.pivot(index="key1", columns="key2", values="value_or_code")
    group_order = [g for g in ("G1", "G2a", "G2b", "G3", "G4", "G5", "G6") if g in pivot.columns]
    st.dataframe(pivot[group_order], width="stretch")
    _matrix_src = matrix_cells[0]["source_ref"] if matrix_cells else "?"
    st.caption(f"{t('col.source')}: {_matrix_src}")

# --------------------------------------------------------------------------- D4
with tab_d4:
    st.subheader(t("glossary.d4_header"))
    st.caption(t("glossary.d4_caption"))
    d4_df = pd.DataFrame([
        {
            t("col.row_type"): r["row_type"],
            t("col.code"): r["name_or_code"],
            t("col.category"): r["category"],
            t("col.description"): r["description"],
            t("col.confirmation_status"): r["confirmation_status"],
            t("col.source"): r["source_ref"],
        }
        for r in read_csv_rows("D4_procedure.csv")
    ])
    st.dataframe(d4_df, hide_index=True, width="stretch")

# --------------------------------------------------------------------------- Nghi vấn & Xác nhận
with tab_oq:
    st.caption(t("glossary.oq_caption"))

    _STATUS_LABEL = {
        STATUS_UNVERIFIED: t("glossary.oq_status_unverified"),
        STATUS_RESOLVED: t("glossary.oq_status_resolved"),
        STATUS_PROPOSED: t("glossary.oq_status_proposed"),
    }
    _FILTER_OPTIONS = {
        t("glossary.oq_filter_all"): None,
        t("glossary.oq_status_unverified"): STATUS_UNVERIFIED,
        t("glossary.oq_status_resolved"): STATUS_RESOLVED,
        t("glossary.oq_status_proposed"): STATUS_PROPOSED,
    }
    chosen_label = st.radio(
        t("glossary.oq_filter_label"), options=list(_FILTER_OPTIONS.keys()), horizontal=True, key="oq_status_filter",
    )
    chosen_bucket = _FILTER_OPTIONS[chosen_label]

    _lang = get_lang()
    for section_id, section_titles in SECTIONS.items():
        rows = [q for q in QUESTIONS if q.section == section_id and (chosen_bucket is None or q.status_bucket == chosen_bucket)]
        if not rows:
            continue
        st.subheader(section_titles.get(_lang) or section_titles["vi"])
        oq_df = pd.DataFrame([
            {
                t("glossary.oq_col_id"): q.id,
                t("glossary.oq_col_status"): f"{_STATUS_LABEL[q.status_bucket]} ({q.status_raw})",
                t("glossary.oq_col_content"): (q.text_ja if _lang == "ja" else q.text_vi) or q.text_vi,
                t("glossary.oq_col_owner"): (q.owner_ja if _lang == "ja" else q.owner_vi) or q.owner_vi,
            }
            for q in rows
        ])
        st.dataframe(oq_df, hide_index=True, width="stretch")

    st.caption(t("glossary.oq_source"))

st.divider()
v1, v2, v3, v4 = st.columns(4)
v1.metric("D1", dicts.d1.version)
v2.metric("D2", dicts.d2.version)
v3.metric("D3", dicts.d3.version)
v4.metric("D4", dicts.d4.version)
st.caption(t("glossary.version_footer"))
