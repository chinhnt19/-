"""source_record_ref construction (Session 05 §3.4) -- unhashed references
to the real primary key of the source table, used so a reviewer can look
the row back up in ORCA. Never hashed/anonymized (operational need, not PII
-- patient_name is the only PII, and it never appears here)."""
from __future__ import annotations


def disease_source_ref(clinic_id: str, patient_id: str, perform_month: str, disease_name: str, in_out) -> str:
    return f"disease_records|{clinic_id}|{patient_id}|{perform_month}|{disease_name}|{in_out or ''}"


def medical_source_ref(clinic_id: str, patient_id: str, perform_month: str, medication_code, in_out) -> str:
    return f"medical_records|{clinic_id}|{patient_id}|{perform_month}|{medication_code}|{in_out or ''}"


def medical_points_source_ref(clinic_id: str, patient_id: str, perform_month: str, medical_day, medical_class) -> str:
    return f"medical_points|{clinic_id}|{patient_id}|{perform_month}|{medical_day}|{medical_class}"
