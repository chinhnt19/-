"""Load D1-D4 from dictionaries/*.csv (verbatim copies of
deliverables/session03/*.csv -- do not hand-edit; regenerate by re-copying
from Session 03 if that deliverable changes version).

CLAUDE.md mục 4: "Keep dictionaries and search conditions in external
version-controlled files." Nothing in this module invents a term that is
not already literally present in the CSV cells it reads.
"""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from services.normalize import nfkc

DICT_DIR = Path(__file__).resolve().parents[1] / "dictionaries"


# --------------------------------------------------------------------------- D1
@dataclass(frozen=True)
class D1Modifier:
    id: str
    pattern: str
    status: str  # X|H|S|A


@dataclass(frozen=True)
class D1Category:
    id: str
    order: int
    code: str  # Q,K,T,F,N,PV,PA,PL,PS,PB,PG,LB,BI,UR,VI,O,R,Z
    name_jp: str
    pattern_text: str  # raw prose cell, kept for traceability/tooltip display


@dataclass(frozen=True)
class D1MatchTerm:
    d1_code: str
    match_type: str
    term: str


@dataclass(frozen=True)
class D1Dictionary:
    version: str
    modifiers: list[D1Modifier]
    categories: list[D1Category]  # sorted by order, 1..18
    match_terms: dict[str, list[D1MatchTerm]]  # d1_code -> MATCH_TERM rows
    exclusion_terms: dict[str, list[str]]  # d1_code -> EXCLUSION_TERM terms


_MODIFIER_PRIORITY = {"X": 0, "H": 1, "S": 2, "A": 3}  # lower = higher priority


def modifier_priority(status: str) -> int:
    return _MODIFIER_PRIORITY.get(status, 99)


def load_d1(path: Path = DICT_DIR / "D1_disease.csv") -> D1Dictionary:
    modifiers: list[D1Modifier] = []
    categories: list[D1Category] = []
    match_terms: dict[str, list[D1MatchTerm]] = {}
    exclusion_terms: dict[str, list[str]] = {}
    version = "unknown"

    with open(path, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            version = row["version"] or version
            row_type = row["row_type"]
            if row_type == "MODIFIER":
                modifiers.append(D1Modifier(id=row["id"], pattern=row["pattern_or_term"], status=row["status"]))
            elif row_type == "CATEGORY":
                categories.append(D1Category(
                    id=row["id"], order=int(row["order"]), code=row["d1_category"],
                    name_jp=row["category_name_jp"], pattern_text=row["pattern_or_term"],
                ))
            elif row_type == "MATCH_TERM":
                code = row["d1_category"]
                match_terms.setdefault(code, []).append(
                    D1MatchTerm(d1_code=code, match_type=row["match_type"], term=row["pattern_or_term"])
                )
            elif row_type == "EXCLUSION_TERM":
                code = row["d1_category"]
                exclusion_terms.setdefault(code, []).append(row["exclusion_term"])

    categories.sort(key=lambda c: c.order)
    return D1Dictionary(
        version=version, modifiers=modifiers, categories=categories,
        match_terms=match_terms, exclusion_terms=exclusion_terms,
    )


@lru_cache(maxsize=None)
def parse_or_term_list(prose: str) -> tuple[str, ...]:
    """Extract an OR-of-substrings term list from a category's prose cell,
    for the categories whose condition is a plain "X・Y・Zを含む" list with no
    AND/exclusion clause (K, T, F, N, PA, PL, UR -- see services/match_d1.py
    docstring for which categories use this vs. a hand-coded rule).

    Splits on "・", strips a trailing "を含む"/"を含み", and unwraps a single
    parenthetical alternate term "親（代替）" into 2 separate OR terms. Does
    NOT handle parenthetical exclusion clauses ("...を除く") -- those
    categories (PV, VI) are hand-coded instead, not run through this parser.
    """
    text = prose.strip()
    for suffix in ("を含む", "を含み"):
        if text.endswith(suffix):
            text = text[: -len(suffix)]
            break
    terms: list[str] = []
    for chunk in text.split("・"):
        chunk = chunk.strip().strip("「」")
        m = re.match(r"^(.*)（(.*)）$", chunk)  # "親（代替）" full-width parens
        if m:
            terms.append(m.group(1).strip("「」"))
            terms.append(m.group(2).strip("「」"))
        elif chunk:
            terms.append(chunk)
    return tuple(terms)


# --------------------------------------------------------------------------- D2
@dataclass(frozen=True)
class D2SearchTerm:
    ingredient_id: str
    confirmed_status: str  # "A" (確認済) | "U" (未確認)
    ingredient_name_jp: str
    search_term: str
    group: str  # G1,G2a,G2b,G3,G4,G5,G6 (7 groups)
    needs_form_check: bool


@dataclass(frozen=True)
class D2Dictionary:
    version: str
    search_terms: list[D2SearchTerm]


_CONFIRMED_STATUS_MAP = {"確認済": "A", "未確認": "U"}


def load_d2(path: Path = DICT_DIR / "D2_antibiotic.csv") -> D2Dictionary:
    terms: list[D2SearchTerm] = []
    version = "unknown"
    with open(path, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if row["row_type"] != "SEARCH_TERM":
                continue
            version = row["version"] or version
            terms.append(D2SearchTerm(
                ingredient_id=row["ingredient_id"],
                confirmed_status=_CONFIRMED_STATUS_MAP.get(row["confirmed_status"], "U"),
                ingredient_name_jp=row["ingredient_name_jp"],
                search_term=nfkc(row["search_term"]),
                group=row["group"],
                # "要剤形確認" ("dosage-form confirmation needed") lives in the
                # search_term_type column (e.g. A03 ユナシン = "販・要剤形確認"),
                # not in notes -- notes only explains WHY in free text.
                needs_form_check="要剤形確認" in (row["search_term_type"] or ""),
            ))
    return D2Dictionary(version=version, search_terms=terms)


# --------------------------------------------------------------------------- D3
@dataclass(frozen=True)
class D3Dictionary:
    version: str
    groups: dict[str, str]  # G1,G2a,G2b,G3,G4,G5,G6 (7 groups) -> description
    judgment_codes: dict[str, str]  # A/B/C/X -> description
    matrix: dict[tuple[str, str], str]  # (row_key, group) -> code
    application_rules: dict[str, str]  # APPLY-1..5 -> description


def load_d3(path: Path = DICT_DIR / "D3_judgment.csv") -> D3Dictionary:
    groups: dict[str, str] = {}
    judgment_codes: dict[str, str] = {}
    matrix: dict[tuple[str, str], str] = {}
    application_rules: dict[str, str] = {}
    version = "unknown"
    with open(path, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            version = row["version"] or version
            row_type = row["row_type"]
            if row_type == "ANTIBIOTIC_GROUP":
                groups[row["key1"]] = row["value_or_code"]
            elif row_type == "JUDGMENT_CODE":
                judgment_codes[row["key1"]] = row["value_or_code"]
            elif row_type == "MATRIX_CELL":
                matrix[(row["key1"], row["key2"])] = row["value_or_code"]
            elif row_type == "APPLICATION_RULE":
                application_rules[row["key1"]] = row["description"]
    return D3Dictionary(
        version=version, groups=groups, judgment_codes=judgment_codes,
        matrix=matrix, application_rules=application_rules,
    )


# --------------------------------------------------------------------------- D4
@dataclass(frozen=True)
class D4Entry:
    row_type: str
    id: str
    category: str
    name_or_code: str
    description: str
    evidence_type: str
    confirmation_status: str


@dataclass(frozen=True)
class D4Dictionary:
    version: str
    entries: list[D4Entry]


def load_d4(path: Path = DICT_DIR / "D4_procedure.csv") -> D4Dictionary:
    entries: list[D4Entry] = []
    version = "unknown"
    with open(path, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            version = row["version"] or version
            entries.append(D4Entry(
                row_type=row["row_type"], id=row["id"], category=row["category"],
                name_or_code=row["name_or_code"], description=row["description"],
                evidence_type=row["evidence_type"], confirmation_status=row["confirmation_status"],
            ))
    return D4Dictionary(version=version, entries=entries)


# --------------------------------------------------------------------------- D5 (DRAFT addendum 2026-11-05)
@dataclass(frozen=True)
class D5ContextFlag:
    id: str
    code: str
    description: str


@dataclass(frozen=True)
class D5Dictionary:
    version: str
    flags: list[D5ContextFlag]


def load_d5(path: Path = DICT_DIR / "D5_context_flags.csv") -> D5Dictionary:
    """D5 is a DRAFT, unapproved dictionary (see dictionary_specification.md
    §9) -- unlike D1-D4 it was never cross-checked against the Master
    Document. Used for UI reference/display of the 12 context_review_flags
    codes only; nothing in this app auto-fills or validates a candidate's
    context_review_flags value against this list."""
    flags: list[D5ContextFlag] = []
    version = "unknown"
    with open(path, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if row["row_type"] != "CONTEXT_FLAG":
                continue
            version = row["version"] or version
            flags.append(D5ContextFlag(id=row["id"], code=row["name_or_code"], description=row["description"]))
    return D5Dictionary(version=version, flags=flags)


@dataclass(frozen=True)
class AllDictionaries:
    d1: D1Dictionary
    d2: D2Dictionary
    d3: D3Dictionary
    d4: D4Dictionary


def load_all() -> AllDictionaries:
    return AllDictionaries(d1=load_d1(), d2=load_d2(), d3=load_d3(), d4=load_d4())
