"""Small synthetic DataFrames used by multiple tests -- NOT real patient
data. Shapes mirror the real disease_records/medical_records schema
(Session 02 §3)."""
from __future__ import annotations

import pandas as pd


def disease_df(rows: list[dict]) -> pd.DataFrame:
    base = {"clinic_id": "clinic_test", "patient_id": "P1", "perform_month": "2026-05",
            "disease_code": "1234567", "start_date": "2026-05-01", "in_out": "", "fetched_at": "2026-05-15T00:00:00"}
    return pd.DataFrame([{**base, **r} for r in rows])


def medical_df(rows: list[dict]) -> pd.DataFrame:
    base = {"clinic_id": "clinic_test", "patient_id": "P1", "perform_month": "2026-05",
            "medication_code": "123456789", "medical_class": "33", "medical_class_name": "点滴注射",
            "perform_count": 1, "in_out": "", "fetched_at": "2026-05-15T00:00:00"}
    return pd.DataFrame([{**base, **r} for r in rows])
