"""Block 1 -- Database Overview. Rendered as the default page by Home.py's
st.navigation() router (not run directly -- `streamlit run app/Home.py` is
still the documented entrypoint)."""
import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

from _bootstrap import get_connection, get_clinic_master_cached, get_dictionaries, known_clinic_ids

import pandas as pd
import streamlit as st

from database.db_access import (
    get_distinct_patient_count, get_fetched_at_range, get_patient_counts_by_clinic, get_table_row_counts,
)
from rules.clinic_tool_mapping import NAHT_CLINIC_IDS, ZERO_DATA_CLINIC_IDS, clinic_group
from services.i18n import language_selector, t

st.set_page_config(page_title="AGRI CARE Phase 0 — Cohort Tool", layout="wide")
language_selector()
st.title("AGRI CARE — Phase 0 Cohort Analysis Tool")
st.caption(t("home.caption"))

conn = get_connection()
clinics = get_clinic_master_cached()
dicts = get_dictionaries()
counts = get_table_row_counts(conn)
n_patients = get_distinct_patient_count(conn)
patient_counts = get_patient_counts_by_clinic(conn)

st.success(t("home.db_connected"))

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric(t("home.metric_clinic"), len(clinics))
c2.metric(t("home.metric_patients"), f"{n_patients:,}", help=t("home.metric_patients_help"))
c3.metric(t("home.metric_disease"), f"{counts['disease_records']:,}")
c4.metric(t("home.metric_medical"), f"{counts['medical_records']:,}")
c5.metric(t("home.metric_points"), f"{counts['medical_points']:,}", help=t("home.metric_points_help"))

st.divider()
st.subheader(t("home.scope_header"))
st.caption(t("home.scope_caption"))

naht_min, naht_max = get_fetched_at_range(conn, sorted(NAHT_CLINIC_IDS))
homis_ids = [c for c in clinics["clinic_id"] if c not in NAHT_CLINIC_IDS]
homis_min, homis_max = get_fetched_at_range(conn, homis_ids)

freshness = pd.DataFrame([
    {t("col.group"): t("home.group_naht"), "fetched_at min": naht_min or "NA", "fetched_at max": naht_max or "NA"},
    {t("col.group"): t("home.group_homis"), "fetched_at min": homis_min or "NA", "fetched_at max": homis_max or "NA"},
])
st.table(freshness)

st.divider()
st.subheader(t("home.clinic_list_header"))
patient_counts = patient_counts.set_index("clinic_id")["n_patients"].to_dict()
rows = []
for r in clinics.itertuples(index=False):
    n = patient_counts.get(r.clinic_id, 0)
    rows.append({
        "clinic_id": r.clinic_id, "clinic_name": r.clinic_name,
        t("col.group"): clinic_group(r.clinic_id, known_clinic_ids()),
        t("home.col_patient_count"): n,
        t("home.col_notes"): (t("home.note_zero_data") if r.clinic_id in ZERO_DATA_CLINIC_IDS
                               else (t("home.note_small_clinic") if 0 < n < 30 else "")),
    })
df = pd.DataFrame(rows).sort_values([t("col.group"), t("home.col_patient_count")], ascending=[True, False])
st.dataframe(df, width="stretch", hide_index=True)

st.divider()
st.subheader(t("home.dict_version_header"))
v1, v2, v3, v4 = st.columns(4)
v1.metric(t("home.metric_d1"), dicts.d1.version)
v2.metric(t("home.metric_d2"), dicts.d2.version)
v3.metric(t("home.metric_d3"), dicts.d3.version)
v4.metric(t("home.metric_d4"), dicts.d4.version)
st.caption(t("glossary.version_footer"))

st.page_link("pages/1_Tim_kiem.py", label=t("home.link_search"), icon="🔎")
st.page_link("pages/6_Giai_thich_thuat_ngu.py", label=t("home.link_glossary"), icon="📖")
