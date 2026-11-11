"""Entry point -- streamlit run app/Home.py.

Builds routing via st.navigation(pages, position="hidden") -- Streamlit's
OWN auto-rendered sidebar labels were observed (2026-11-08) to lag behind
st.session_state["lang"] after a page-switch click (a known class of
Streamlit issue: native nav chrome doesn't reliably re-render dynamic
`title=` text every rerun). Routing itself (session/state handling) is
unaffected by that -- only the *visible label text* lagged -- so routing
still goes through st.navigation, but the VISIBLE sidebar list is instead
drawn by hand with st.sidebar.page_link(), which (like every other t()-
driven label in this app) reliably re-renders on every rerun.
"""
import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent
_ROOT_DIR = _APP_DIR.parent
for _p in (_APP_DIR, _ROOT_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import streamlit as st

from services.i18n import t

PAGE_DEFS = [
    ("_home_page.py", "nav.home", "🏠", None),
    ("pages/1_Tim_kiem.py", "nav.search", "🔎", "tim-kiem"),
    ("pages/2_Thong_ke.py", "nav.stats", "📊", "thong-ke"),
    ("pages/3_Danh_sach_ung_vien.py", "nav.candidates", "📋", "danh-sach-ung-vien"),
    ("pages/4_Chi_tiet_benh_nhan.py", "nav.detail", "🔍", "chi-tiet-benh-nhan"),
    ("pages/5_Xuat_du_lieu.py", "nav.export", "📤", "xuat-du-lieu"),
    ("pages/6_Giai_thich_thuat_ngu.py", "nav.glossary", "📖", "giai-thich-thuat-ngu"),
]

pages = [
    st.Page(path, title=t(key), icon=icon, default=(url_path is None), **({"url_path": url_path} if url_path else {}))
    for path, key, icon, url_path in PAGE_DEFS
]
pg = st.navigation(pages, position="hidden")

with st.sidebar:
    for path, key, icon, _url_path in PAGE_DEFS:
        st.page_link(path, label=t(key), icon=icon)

pg.run()
