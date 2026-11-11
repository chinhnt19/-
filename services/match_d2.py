"""D2 -- injectable-antibiotic name matching (record-level, medical_records).

session4/01_search_logic_specification_vn.md §6.1 step 5 / Q20 in
rules/q_conditions.json: substring (OR) match against all 89 D2 search
terms. A hit whose search term is flagged `needs_form_check` (e.g. A03
"ユナシン", A17 "ゾシン") is NOT auto-rejected -- it is only flagged, per
Q20's post_processing_vn, for mandatory manual confirmation before being
treated as a confirmed positive.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache

from services.dictionaries import D2Dictionary, D2SearchTerm
from services.normalize import nfkc


@dataclass(frozen=True)
class D2Hit:
    # D2_antibiotic.csv has no per-search-term id column, only ingredient_id
    # (repeated across a term's several brand/generic spellings) -- so per
    # 09_data_dictionary_vn.csv (both d2_search_term_id and d2_ingredient_id
    # use the same A01-A41|U01-U09 vocabulary, and the sample row sets them
    # equal), search_term_id IS the ingredient_id here.
    search_term_id: str
    ingredient_id: str
    group: str
    confirmed_status: str  # A|U
    needs_form_check: bool
    matched_search_term: str


@lru_cache(maxsize=None)
def _fast_reject_pattern(search_terms: tuple[str, ...]) -> re.Pattern:
    """A single compiled "any of these 89 substrings" regex, used only to
    cheaply reject the (large majority of) rows with zero D2 hits before
    paying for the full per-term loop below. Purely a performance guard --
    matching semantics are identical to the plain loop, just faster on the
    common negative case over 3M+ medical_records rows."""
    return re.compile("|".join(re.escape(t) for t in search_terms if t))


def match_d2(medication_name: str, d2: D2Dictionary) -> list[D2Hit]:
    norm = nfkc(medication_name) or ""
    pattern = _fast_reject_pattern(tuple(t.search_term for t in d2.search_terms))
    if not pattern.search(norm):
        return []
    hits: list[D2Hit] = []
    for term in d2.search_terms:
        if term.search_term and term.search_term in norm:
            hits.append(D2Hit(
                search_term_id=term.ingredient_id,
                ingredient_id=term.ingredient_id,
                group=term.group,
                confirmed_status=term.confirmed_status,
                needs_form_check=term.needs_form_check,
                matched_search_term=term.search_term,
            ))
    return hits
