"""D1 -- disease-name classification (record-level).

Implements dictionary_specification.md §4 and
03_candidate_extraction_algorithm_vn.md §4, strictly in this order:
  1. NFKC-normalize the disease name.
  2. Apply the 8 modifier regexes (M01-M08); if several match, priority is
     X (prevention) > H (past/treated) > S (suspected) > A (active). For
     every modifier except M08 the matched suffix is stripped to get the
     "stem" -- used ONLY for category Q's exact match (step 3 below); every
     other category matches against the full normalized name, suffix and
     all (per the pseudocode's `category_rule_matches(cat, disease_name_norm)`
     call, which passes the full normalized name, not the stem).
  3. Try the 18 categories in `order` 1->18, stop at the first match.
  4. Categories in state H or X are the caller's responsibility to drop
     before D3 (03_... §4 note) -- this module only classifies, it does not
     filter.

Known open discrepancy (documented here, not silently resolved -- CLAUDE.md
mục 3 "Never invent... Do not silently modify"): D1_disease.csv labels the
BI category's MATCH_TERM rows `match_type=exact(stem)`, identical to Q's
label, but dictionary_specification.md §4 step 3 and the Session 04
pseudocode both state that only Q uses the modifier-stripped stem and every
other category (including BI) matches the full normalized name. This module
follows the more detailed/explicit algorithmic source (spec text +
pseudocode) for BI, i.e. BI matches on the full normalized name. Flagged in
the Implementation Traceability Report for the research team to resolve.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from services.dictionaries import D1Dictionary, D1MatchTerm, modifier_priority, parse_or_term_list
from services.normalize import nfkc

# Categories whose condition is a plain "X・Y・Zを含む" OR-of-substrings prose
# cell with no AND/exclusion clause -- handled by the generic prose parser.
_SIMPLE_OR_PROSE_CODES = {"K", "T", "F", "N", "PA", "PL", "UR"}


@dataclass(frozen=True)
class D1MatchResult:
    category: str  # one of the 18 D1 codes
    state: str  # A|S|H|X
    matched_modifier_id: str | None
    stem_used: str
    disease_name_norm: str


def _strip_matched_suffix(text: str, pattern: str) -> str:
    m = re.search(pattern, text)
    if not m:
        return text
    return text[: m.start()] + text[m.end():]


def _term_matches(text: str, match_type: str, term: str) -> bool:
    if match_type == "contains":
        return term in text
    if match_type == "regex":
        return re.search(term, text) is not None
    if match_type in ("exact", "exact(stem)"):
        return text == term
    raise ValueError(f"Unknown D1 MATCH_TERM match_type: {match_type!r}")


def _any_term_matches(text: str, rows: list[D1MatchTerm]) -> bool:
    return any(_term_matches(text, r.match_type, r.term) for r in rows)


def _match_pv(text: str) -> bool:
    """D1-06 PV -- "COVID-19・コロナ・インフルエンザ（「インフルエンザ菌」を除く）・
    RSウイルス・「ウイルス性」と「肺炎」を含む" (D1_disease.csv row D1-06)."""
    if "COVID-19" in text or "コロナ" in text or "RSウイルス" in text:
        return True
    if "インフルエンザ" in text and "インフルエンザ菌" not in text:
        return True
    if "ウイルス性" in text and "肺炎" in text:
        return True
    return False


def _match_vi(text: str) -> bool:
    """D1-15 VI -- "COVID-19・コロナウイルス・インフルエンザ（菌を除く）・
    RSウイルス・「ウイルス感染症」・サイトメガロウイルスを含む" (row D1-15)."""
    if any(t in text for t in ("COVID-19", "コロナウイルス", "RSウイルス", "ウイルス感染症", "サイトメガロウイルス")):
        return True
    if "インフルエンザ" in text and "インフルエンザ菌" not in text:
        return True
    return False


def _match_ps(text: str) -> bool:
    """D1-09 PS -- "病名に「誤嚥性肺炎」を含む" (row D1-09)."""
    return "誤嚥性肺炎" in text


def _match_pg(text: str) -> bool:
    """D1-11 PG -- "上記・下記のどれにも当たらず「肺炎」を含む" (row D1-11).
    The "not matched by any other category" part is automatically satisfied
    by strict order-1..18 evaluation (PG sits at order 11, after every other
    肺炎-related category) -- so the condition actually implemented here is
    just "contains 肺炎"."""
    return "肺炎" in text


def _match_pb(text: str, rows: list[D1MatchTerm]) -> bool:
    """D1-10 PB -- match_type 'contains(+肺炎)': causative-organism term
    AND "肺炎" both present (row group D1-3)."""
    if "肺炎" not in text:
        return False
    return any(r.term in text for r in rows)


def _match_o(text: str, match_rows: list[D1MatchTerm], exclusion_terms: list[str]) -> bool:
    if any(excl in text for excl in exclusion_terms):
        return False
    return _any_term_matches(text, match_rows)


def _match_q(stem: str, rows: list[D1MatchTerm]) -> bool:
    return any(stem == r.term for r in rows)


def _category_matches(code: str, text: str, stem: str, d1: D1Dictionary, category_pattern_text: str) -> bool:
    if code == "Q":
        return _match_q(stem, d1.match_terms.get("Q", []))
    if code == "PV":
        return _match_pv(text)
    if code == "VI":
        return _match_vi(text)
    if code == "PS":
        return _match_ps(text)
    if code == "PG":
        return _match_pg(text)
    if code == "PB":
        return _match_pb(text, d1.match_terms.get("PB", []))
    if code == "O":
        return _match_o(text, d1.match_terms.get("O", []), d1.exclusion_terms.get("O", []))
    if code in ("LB", "BI", "R"):
        return _any_term_matches(text, d1.match_terms.get(code, []))
    if code in _SIMPLE_OR_PROSE_CODES:
        return any(term in text for term in parse_or_term_list(category_pattern_text))
    if code == "Z":
        return True  # catch-all, must be last in `order`
    raise ValueError(f"No D1 matcher implemented for category code {code!r}")


def classify_d1(disease_name: str, d1: D1Dictionary) -> D1MatchResult:
    norm = nfkc(disease_name) or ""

    matched_modifiers = [m for m in d1.modifiers if re.search(m.pattern, norm)]
    if matched_modifiers:
        chosen = min(matched_modifiers, key=lambda m: modifier_priority(m.status))
        state = chosen.status
        stem = norm if chosen.id == "M08" else _strip_matched_suffix(norm, chosen.pattern)
        matched_modifier_id = chosen.id
    else:
        state = "A"
        stem = norm
        matched_modifier_id = None

    for cat in d1.categories:  # pre-sorted by `order` 1..18
        if _category_matches(cat.code, norm, stem, d1, cat.pattern_text):
            return D1MatchResult(
                category=cat.code, state=state, matched_modifier_id=matched_modifier_id,
                stem_used=stem, disease_name_norm=norm,
            )

    # Unreachable in practice because D1-18 (Z) is a catch-all, kept only as
    # a defensive fallback.
    return D1MatchResult(category="Z", state=state, matched_modifier_id=matched_modifier_id,
                          stem_used=stem, disease_name_norm=norm)
