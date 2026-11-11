"""Clinic -> crawl-tool-group (NAHT/HOMIS) mapping.

Source of truth: document/A/clinic_tool_mapping_v1.0.md (v1.0, confirmed by
project owner 2026-11-04). The NAHT list below is the explicit 11-clinic
roster from that document (cross-checked 1:1 against document/A/NAHT.txt).
HOMIS is NOT a separate explicit list -- it is defined by exclusion (every
clinic_id not in NAHT_CLINIC_IDS), exactly as the mapping document specifies.

Do NOT fall back to a `clinic_id LIKE 'clinic_cl%'` pattern for new clinics
that are not yet in this list -- clinic_tool_mapping_v1.0.md explicitly warns
that pattern is an observation, not a durable rule. Any clinic_id not found
here must be flagged for confirmation with the project owner, never silently
classified by name pattern.
"""
from __future__ import annotations

NAHT_CLINIC_IDS: frozenset[str] = frozenset({
    "clinic_hitachi",
    "clinic_fujisawa",
    "clinic_utsunomiya",
    "clinic_setagaya",
    "clinic_tochigi",
    "clinic_kasukabe",
    "clinic_mooka",
    "clinic_kiyosu",
    "clinic_nishitoukyou",
    "clinic_matsudo",
    "clinic_sanjou",
})

# clinic_cl250 (しおや) has 0 rows in all 3 source tables -- confirmed by the
# project owner (2026-11-04) to be "not an issue", just an unregistered-but-
# empty clinic. Session 02 rule: exclude it from the denominator when
# computing facility-level rates/percentages. It still belongs to HOMIS (by
# exclusion) and must still be listed in the UI, just annotated as 0-row.
ZERO_DATA_CLINIC_IDS: frozenset[str] = frozenset({"clinic_cl250"})

# OPEN-05-01 (Session 05): a candidate_id is close to re-identifying an
# individual at a very small facility (e.g. clinic_sanjou has 16 patients
# total). The dashboard must show a warning banner below this threshold --
# it must NOT block any action on its own (no approved access-control policy
# exists yet).
SMALL_FACILITY_PATIENT_THRESHOLD = 30

ToolGroup = str  # "NAHT" | "HOMIS"


class UnmappedClinicError(ValueError):
    """Raised when a clinic_id is not yet classified and must be confirmed
    with the project owner before being used in NAHT/HOMIS aggregates."""


def clinic_group(clinic_id: str, known_clinic_ids: frozenset[str] | None = None) -> ToolGroup:
    """Return 'NAHT' or 'HOMIS' for a clinic_id.

    `known_clinic_ids`, when given (e.g. the current clinic_master contents),
    is used only to decide whether a clinic outside NAHT_CLINIC_IDS is a
    *known* HOMIS clinic or an entirely unseen clinic_id that needs human
    confirmation first (clinic_tool_mapping_v1.0.md mục 5).
    """
    if clinic_id in NAHT_CLINIC_IDS:
        return "NAHT"
    if known_clinic_ids is not None and clinic_id not in known_clinic_ids:
        raise UnmappedClinicError(
            f"clinic_id '{clinic_id}' is not in NAHT_CLINIC_IDS and not present in the "
            "supplied known_clinic_ids snapshot -- confirm with the project owner before "
            "classifying it as HOMIS (see document/A/clinic_tool_mapping_v1.0.md mục 5)."
        )
    return "HOMIS"


def is_zero_data_clinic(clinic_id: str) -> bool:
    return clinic_id in ZERO_DATA_CLINIC_IDS
