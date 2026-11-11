"""QC1 / QC2 (provisional Set-C definitions, DEC-04-01) and Q40 outcome
hints (confirmed), all record-level over medical_records.

QC1/QC2 are explicitly 暫定 (provisional) -- NOT part of the official
Master Document Table 7-1 -- per DEC-04-01. Every place that surfaces them
must carry that label; this module itself does not render UI, but callers
must not drop the label.
"""
from __future__ import annotations

from services.normalize import nfkc
from rules.q_conditions import (
    QC1_INJECTION_MEDICAL_CLASSES,
    QC2_C005_2_NAME_CANDIDATE,
    Q40_OUTCOME_HINT_TERMS,
)


def match_qc1(medical_class: str | None) -> bool:
    return medical_class in QC1_INJECTION_MEDICAL_CLASSES


def match_qc2(medication_name: str | None) -> bool:
    """OPEN-04-01: the exact ORCA string for billing item C005-2 is NOT
    verified against real data. A positive match here must be reported as
    the UNCONFIRMED token, never as a plain "Y" (see
    09_data_dictionary_vn.csv, in_set_c_narrow_qc2)."""
    norm = nfkc(medication_name) or ""
    return QC2_C005_2_NAME_CANDIDATE in norm


def match_q40_hints(medication_name: str | None) -> list[str]:
    """Returns the subset of D4-3 (P20-P24) outcome-hint terms found in this
    record. Clue only -- never implies a confirmed outcome (CLAUDE.md mục 3,
    02_q_conditions.json Q40.important_caveat)."""
    norm = nfkc(medication_name) or ""
    return [term for term in Q40_OUTCOME_HINT_TERMS if term in norm]
