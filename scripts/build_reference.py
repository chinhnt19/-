"""ETL: query orca_snapshot.db once, write small precomputed CSVs into reference/.

Run with: ./.venv/bin/python scripts/build_reference.py
Re-run only when orca_snapshot.db changes.
"""
import calendar
import csv
import re
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "orca_snapshot.db"
DOC_DIR = ROOT / "document"
REF_DIR = ROOT / "reference"
REF_DIR.mkdir(exist_ok=True)

# Known substring collisions that are NOT the intended drug (data-matching
# safeguard, not a clinical route exclusion). Add more here if found later.
FALSE_POSITIVE_GUARD = {
    "ゾシン": ["ドキサゾシン"],  # Doxazosin (BP drug) contains "ゾシン" but is unrelated
}


def month_bounds(perform_month: str):
    year, month = (int(x) for x in perform_month.split("-"))
    first = f"{year:04d}-{month:02d}-01"
    last_day = calendar.monthrange(year, month)[1]
    last = f"{year:04d}-{month:02d}-{last_day:02d}"
    return first, last


def compress_month_ranges(months) -> str:
    """Collapse a list of 'YYYY-MM' strings into consecutive-month ranges,
    e.g. ['2025-06',...,'2026-08'] -> '2025-06 → 2026-08' instead of listing
    every month."""

    def to_tuple(m):
        y, mo = m.split("-")
        return int(y), int(mo)

    def next_month(y, mo):
        return (y, mo + 1) if mo < 12 else (y + 1, 1)

    def fmt(t):
        return f"{t[0]:04d}-{t[1]:02d}"

    uniq = sorted({to_tuple(m) for m in months})
    if not uniq:
        return ""

    ranges = []
    start = prev = uniq[0]
    for cur in uniq[1:]:
        if cur == next_month(*prev):
            prev = cur
        else:
            ranges.append((start, prev))
            start = prev = cur
    ranges.append((start, prev))

    return ", ".join(fmt(s) if s == e else f"{fmt(s)} → {fmt(e)}" for s, e in ranges)


def load_antibiotics_terms():
    """Build a flat list of (term, group_en, generic_en, generic_jp) to match against medication_name."""
    terms = []
    with open(DOC_DIR / "antibiotics_reference.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            group_en = row["group_en"].strip()
            generic_en = row["generic_en"].strip()
            generic_jp = row["generic_jp"].strip()
            brand_jp = row["brand_jp"].strip()
            candidates = {generic_jp}
            for b in brand_jp.split(","):
                b = b.strip()
                if b and "generic" not in b and "não brand" not in b and "(" not in b:
                    candidates.add(b)
            for term in candidates:
                if term:
                    terms.append(
                        {
                            "term": term,
                            "group_en": group_en,
                            "generic_en": generic_en,
                            "generic_jp": generic_jp,
                        }
                    )
    return terms


def match_antibiotic(medication_name: str, terms):
    for t in terms:
        term = t["term"]
        if term in medication_name:
            guard = FALSE_POSITIVE_GUARD.get(term)
            if guard and any(bad in medication_name for bad in guard):
                continue
            return t
    return None


def main():
    print("Connecting to", DB_PATH)
    conn = sqlite3.connect(DB_PATH)

    clinic_master = pd.read_sql("SELECT clinic_id, clinic_name FROM clinic_master", conn)

    print("Loading medical_records (this is the big table, may take a while)...")
    medical = pd.read_sql(
        "SELECT clinic_id, patient_id, patient_name, perform_month, medication_code, "
        "medication_name, medical_class, medical_class_name, perform_count FROM medical_records",
        conn,
    )
    print(f"  {len(medical):,} rows loaded")

    print("Loading disease_records...")
    disease = pd.read_sql(
        "SELECT clinic_id, patient_id, patient_name, perform_month, disease_name, "
        "disease_code, start_date FROM disease_records",
        conn,
    )
    print(f"  {len(disease):,} rows loaded")
    conn.close()

    # ---- 1. Antibiotics matching ----------------------------------------
    print("Matching antibiotics...")
    terms = load_antibiotics_terms()
    matched = medical["medication_name"].apply(lambda m: match_antibiotic(m, terms))
    is_abx = matched.notna()
    abx = medical[is_abx].copy()
    abx["matched_group_en"] = matched[is_abx].apply(lambda t: t["group_en"])
    abx["matched_generic_en"] = matched[is_abx].apply(lambda t: t["generic_en"])
    abx = abx.merge(clinic_master, on="clinic_id", how="left")
    abx.to_csv(REF_DIR / "antibiotics_patients.csv", index=False)
    print(f"  antibiotics_patients.csv: {len(abx):,} rows")

    abx_patient_keys = set(zip(abx["clinic_id"], abx["patient_id"]))
    print(f"  distinct (clinic, patient) on antibiotics: {len(abx_patient_keys):,}")

    # ---- 2. Clinic overview ----------------------------------------------
    print("Building clinic overview...")
    total_by_clinic = (
        medical.drop_duplicates(["clinic_id", "patient_id"])
        .groupby("clinic_id")
        .size()
        .rename("total_patients")
    )
    abx_by_clinic = (
        abx.drop_duplicates(["clinic_id", "patient_id"])
        .groupby("clinic_id")
        .size()
        .rename("antibiotic_patients")
    )
    overview = clinic_master.set_index("clinic_id").join([total_by_clinic, abx_by_clinic])
    overview["total_patients"] = overview["total_patients"].fillna(0).astype(int)
    overview["antibiotic_patients"] = overview["antibiotic_patients"].fillna(0).astype(int)
    overview = overview[overview["total_patients"] > 0].reset_index()
    overview["pct_antibiotic"] = (
        overview["antibiotic_patients"] / overview["total_patients"] * 100
    ).round(1)
    overview.sort_values("total_patients", ascending=False).to_csv(
        REF_DIR / "clinics.csv", index=False
    )
    print(f"  clinics.csv: {len(overview):,} rows")

    # ---- 3. Filter the two big tables down to the antibiotic patient set --
    print("Filtering medical_records / disease_records to antibiotic patients...")
    key = medical["clinic_id"] + "|" + medical["patient_id"]
    abx_key_set = {f"{c}|{p}" for c, p in abx_patient_keys}
    med_detail = medical[key.isin(abx_key_set)].copy()
    med_detail.to_csv(REF_DIR / "medication_by_month_detail.csv", index=False)
    print(f"  medication_by_month_detail.csv: {len(med_detail):,} rows")

    dkey = disease["clinic_id"] + "|" + disease["patient_id"]
    disease_badges = disease[dkey.isin(abx_key_set)].copy()
    disease_badges.to_csv(REF_DIR / "disease_badges.csv", index=False)
    print(f"  disease_badges.csv: {len(disease_badges):,} rows")

    # ---- 4. ADROP flags (join disease_badges with adrop_reference_flags) --
    print("Building ADROP flags...")
    adrop_ref = pd.read_csv(DOC_DIR / "adrop_reference_flags.csv")
    adrop_ref = adrop_ref[adrop_ref["recommend_include"].isin(["Y", "C"])]
    adrop_ref = adrop_ref[["flag_category", "disease_name_jp", "recommend_include", "reason_vn"]]
    adrop_ref = adrop_ref.rename(columns={"disease_name_jp": "disease_name"})
    flags = disease_badges.merge(adrop_ref, on="disease_name", how="inner")
    flags = flags[
        [
            "clinic_id",
            "patient_id",
            "patient_name",
            "disease_name",
            "start_date",
            "perform_month",
            "flag_category",
            "recommend_include",
            "reason_vn",
        ]
    ]
    flags.to_csv(REF_DIR / "adrop_flags.csv", index=False)
    print(f"  adrop_flags.csv: {len(flags):,} rows")

    # ---- 5. Timeline bounds per patient ------------------------------------
    print("Building timeline bounds...")
    med_detail["month_first"], med_detail["month_last"] = zip(
        *med_detail["perform_month"].map(month_bounds)
    )
    bounds_med = med_detail.groupby(["clinic_id", "patient_id"]).agg(
        med_first=("month_first", "min"), med_last=("month_last", "max")
    )
    bounds_disease = disease_badges.groupby(["clinic_id", "patient_id"]).agg(
        dis_first=("start_date", "min"), dis_last=("start_date", "max")
    )
    bounds = bounds_med.join(bounds_disease, how="outer").reset_index()
    bounds["first_date"] = bounds[["med_first", "dis_first"]].min(axis=1)
    bounds["last_date"] = bounds[["med_last", "dis_last"]].max(axis=1)
    bounds = bounds[["clinic_id", "patient_id", "first_date", "last_date", "med_first", "dis_first"]]
    bounds.to_csv(REF_DIR / "patient_timeline_bounds.csv", index=False)
    print(f"  patient_timeline_bounds.csv: {len(bounds):,} rows")

    # ---- 6. Patient summary (for the patient-list table) -------------------
    print("Building patient summary...")
    patient_name_map = med_detail.drop_duplicates(["clinic_id", "patient_id"])[
        ["clinic_id", "patient_id", "patient_name"]
    ]
    abx_summary = (
        abx.groupby(["clinic_id", "patient_id"])
        .agg(
            antibiotic_list=("matched_generic_en", lambda s: ", ".join(sorted(set(s)))),
            n_antibiotic_records=("medication_name", "size"),
            first_antibiotic_month=("perform_month", "min"),
            last_antibiotic_month=("perform_month", "max"),
        )
        .reset_index()
    )
    home_visit = (
        med_detail[med_detail["medical_class"] == "14"]
        .groupby(["clinic_id", "patient_id"])["perform_month"]
        .apply(compress_month_ranges)
        .rename("home_visit_months")
        .reset_index()
    )
    adrop_summary = (
        flags[flags["recommend_include"] == "Y"]
        .groupby(["clinic_id", "patient_id"])["flag_category"]
        .apply(lambda s: ",".join(sorted(set(s))))
        .rename("adrop_flags_confirmed")
        .reset_index()
    )
    adrop_c_summary = (
        flags[flags["recommend_include"] == "C"]
        .groupby(["clinic_id", "patient_id"])["flag_category"]
        .apply(lambda s: ",".join(sorted(set(s))))
        .rename("adrop_flags_suspected")
        .reset_index()
    )

    summary = patient_name_map.merge(abx_summary, on=["clinic_id", "patient_id"], how="left")
    summary = summary.merge(home_visit, on=["clinic_id", "patient_id"], how="left")
    summary = summary.merge(adrop_summary, on=["clinic_id", "patient_id"], how="left")
    summary = summary.merge(adrop_c_summary, on=["clinic_id", "patient_id"], how="left")
    summary = summary.merge(clinic_master, on="clinic_id", how="left")
    for col in ["home_visit_months", "adrop_flags_confirmed", "adrop_flags_suspected"]:
        summary[col] = summary[col].fillna("")
    summary.to_csv(REF_DIR / "patients_summary.csv", index=False)
    print(f"  patients_summary.csv: {len(summary):,} rows")

    print("Done.")


if __name__ == "__main__":
    main()
