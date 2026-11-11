"""Record-level classification over the raw DataFrames loaded by
database/db_access.py. Every disease_records / medical_records row is
evaluated independently (REQ01/REQ04) -- nothing here groups by patient yet;
that happens in services/aggregate.py.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from services.dictionaries import AllDictionaries
from services.flags import flag_zzz_pending_confirmation
from services.match_d1 import classify_d1
from services.match_d2 import match_d2
from services.match_qc import match_q40_hints, match_qc1, match_qc2
from services.normalize import nfkc
from rules.q_conditions import Q10_D1_CATEGORIES, Q10_D1_STATES


@dataclass
class ClassifiedDiseaseRow:
    clinic_id: str
    patient_id: str
    perform_month: str
    disease_name_original: str
    disease_name_normalized: str
    disease_code: str | None
    flag_zzz_pending_confirmation: bool
    start_date: str | None
    in_out: str | None
    fetched_at: str | None
    d1_matched_modifier_id: str | None
    d1_state: str
    d1_category: str
    d1_category_name_jp: str
    matched_q10: bool


@dataclass
class ClassifiedMedicalRow:
    clinic_id: str
    patient_id: str
    perform_month: str
    medication_name_original: str
    medication_name_normalized: str
    medication_code: str | None
    medical_class: str | None
    medical_class_name: str | None
    perform_count_raw: object
    in_out: str | None
    fetched_at: str | None
    matched_q20: bool
    d2_hits: list = field(default_factory=list)  # list[D2Hit]
    needs_form_check: bool = False
    qc1_wide: bool = False
    qc2_narrow: bool = False
    q40_hints: list[str] = field(default_factory=list)


def classify_disease_rows(df: pd.DataFrame, dicts: AllDictionaries) -> list[ClassifiedDiseaseRow]:
    out: list[ClassifiedDiseaseRow] = []
    d1_name_by_code = {c.code: c.name_jp for c in dicts.d1.categories}
    for r in df.itertuples(index=False):
        result = classify_d1(r.disease_name, dicts.d1)
        matched_q10 = result.category in Q10_D1_CATEGORIES and result.state in Q10_D1_STATES
        out.append(ClassifiedDiseaseRow(
            clinic_id=r.clinic_id, patient_id=r.patient_id, perform_month=r.perform_month,
            disease_name_original=r.disease_name, disease_name_normalized=result.disease_name_norm,
            disease_code=r.disease_code, flag_zzz_pending_confirmation=flag_zzz_pending_confirmation(r.disease_code),
            start_date=r.start_date, in_out=r.in_out, fetched_at=r.fetched_at,
            d1_matched_modifier_id=result.matched_modifier_id, d1_state=result.state,
            d1_category=result.category, d1_category_name_jp=d1_name_by_code.get(result.category, ""),
            matched_q10=matched_q10,
        ))
    return out


def classify_medical_rows(df: pd.DataFrame, dicts: AllDictionaries) -> list[ClassifiedMedicalRow]:
    out: list[ClassifiedMedicalRow] = []
    for r in df.itertuples(index=False):
        d2_hits = match_d2(r.medication_name, dicts.d2)
        out.append(ClassifiedMedicalRow(
            clinic_id=r.clinic_id, patient_id=r.patient_id, perform_month=r.perform_month,
            medication_name_original=r.medication_name, medication_name_normalized=nfkc(r.medication_name),
            medication_code=r.medication_code, medical_class=r.medical_class,
            medical_class_name=r.medical_class_name, perform_count_raw=r.perform_count,
            in_out=r.in_out, fetched_at=r.fetched_at,
            matched_q20=len(d2_hits) > 0, d2_hits=d2_hits,
            needs_form_check=any(h.needs_form_check for h in d2_hits),
            qc1_wide=match_qc1(r.medical_class), qc2_narrow=match_qc2(r.medication_name),
            q40_hints=match_q40_hints(r.medication_name),
        ))
    return out
