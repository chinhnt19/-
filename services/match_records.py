"""Record-level classification over the raw DataFrames loaded by
database/db_access.py. Every disease_records / medical_records row is
evaluated independently -- nothing here groups by patient or by month
yet; that happens in services/build_candidates.py.

v1.3.1: a medical_records row is a *candidate signal* (V1-DRUG AND
V1-ROUTE, rules/q_conditions.json) if it matches an antibiotic drug name
(D2) AND its medical_class is injection-eligible (D4_注射区分, 32/33).
Disease rows are no longer filtered for candidate selection (the old Q10
concept) -- they are only classified (D1) so build_candidates.py can
later tag a candidate's billed-month window with the disease names valid
during it (CSV設計説明書v1.3.1 §6.2).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from services.dictionaries import AllDictionaries
from services.flags import flag_zzz_pending_confirmation
from services.match_d1 import classify_d1
from services.match_d2 import match_d2
from services.normalize import nfkc
from rules.q_conditions import ELIGIBLE_INJECTION_MEDICAL_CLASSES


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
    is_antibiotic_hit: bool
    d2_hits: list = field(default_factory=list)  # list[D2Hit]
    needs_form_check: bool = False
    route_class_a13: str | None = None  # "静注" | "点滴静注" | None (not injection-eligible)

    @property
    def is_candidate_signal(self) -> bool:
        """V1-DRUG AND V1-ROUTE: the row contributes to a candidate only if
        it is both an antibiotic hit and an eligible injection route."""
        return self.is_antibiotic_hit and self.route_class_a13 is not None


def classify_disease_rows(df: pd.DataFrame, dicts: AllDictionaries) -> list[ClassifiedDiseaseRow]:
    out: list[ClassifiedDiseaseRow] = []
    d1_name_by_code = {c.code: c.name_jp for c in dicts.d1.categories}
    for r in df.itertuples(index=False):
        result = classify_d1(r.disease_name, dicts.d1)
        out.append(ClassifiedDiseaseRow(
            clinic_id=r.clinic_id, patient_id=r.patient_id, perform_month=r.perform_month,
            disease_name_original=r.disease_name, disease_name_normalized=result.disease_name_norm,
            disease_code=r.disease_code, flag_zzz_pending_confirmation=flag_zzz_pending_confirmation(r.disease_code),
            start_date=r.start_date, in_out=r.in_out, fetched_at=r.fetched_at,
            d1_matched_modifier_id=result.matched_modifier_id, d1_state=result.state,
            d1_category=result.category, d1_category_name_jp=d1_name_by_code.get(result.category, ""),
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
            is_antibiotic_hit=len(d2_hits) > 0, d2_hits=d2_hits,
            needs_form_check=any(h.needs_form_check for h in d2_hits),
            route_class_a13=ELIGIBLE_INJECTION_MEDICAL_CLASSES.get(r.medical_class),
        ))
    return out
