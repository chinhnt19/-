# AGRI CARE — Phase 0 Cohort Analysis Tool

Candidate-extraction and manual-review-support tool for the Phase 0
retrospective study (home-care injectable-antibiotic use for respiratory
infections). This is **not** a diagnosis or treatment-episode-confirmation
system — see `CLAUDE.md` for the project's governing rules, which this
implementation follows throughout.

## What this is / is not

- Reads `document/B/orca_snapshot.db` **read-only** (SQLite `mode=ro` +
  `PRAGMA query_only = ON`). Nothing in this codebase writes to that file.
- Applies the approved D1 (disease), D2 (injectable antibiotic), D3
  (judgment matrix), D4 (procedure/outcome-hint) dictionaries and the Q
  search conditions exactly as transcribed in `deliverables/session03/` and
  `deliverables/session4/02_q_conditions.json` — copied verbatim into
  `dictionaries/` and `rules/q_conditions.json` respectively.
- Produces the 6 CSVs specified in `deliverables/session05/`: Candidate + 3
  Evidence files (machine-generated, full snapshot per run) and 2 blank
  human-authored templates (Manual Review, Outcome) that this tool never
  writes clinical values into.
- Never infers Day 0, treatment episodes, or 30-day outcomes automatically.
  Those fields only ever exist once a human fills in the Manual
  Review/Outcome templates outside this tool.
- Never exports `patient_name`. `candidate_id = "{clinic_id}:{patient_id}"`
  is the only identifier used throughout (REQ08).

## Architecture

```
app/            Streamlit UI (multipage) — Home.py (Block 1) + pages/ (Blocks 2-7)
database/       Read-only SQLite access (database/db_access.py)
services/       Normalization, dictionary loading, D1/D2/QC/D3 matching, aggregation
dictionaries/   Verbatim copies of D1-D4 CSV (Session 03) — version-controlled
rules/          Q conditions (verbatim JSON copy) + clinic NAHT/HOMIS mapping
models/         Dataclasses + exact CSV column schemas (Session 05)
exports/        Pure functions building the 6 output CSVs as DataFrames
tests/          pytest unit + integration tests
```

Each layer only depends on the layers below it (`app` -> `exports`/`services`
-> `database`/`dictionaries`/`rules` -> `models`), per CLAUDE.md's module
separation requirement.

## Installation

```bash
python3 -m venv .venv            # if not already created
.venv/bin/pip install -r requirements.txt
```

The database file must exist at `document/B/orca_snapshot.db` (already the
case in this project checkout).

## Running

```bash
.venv/bin/streamlit run app/Home.py
```

Then open the printed local URL. Use the sidebar on "Tìm kiếm" to scope the
search (facility, month range), click "CHẠY TÌM KIẾM", and move through
Thống kê → Danh sách ứng viên → Chi tiết → Xuất dữ liệu.

**Performance note:** the matching engine is pure Python (record-by-record,
per CLAUDE.md's "do not over-engineer" guidance for a Phase 0 tool, not a
BI platform). Scanning the single largest clinic (~640k rows) takes ~25s on
a typical laptop; the full un-filtered database (~6.3M rows across 38
clinics) takes several minutes. Narrowing the facility/month filter before
running keeps this fast for day-to-day use.

## Running the tests

```bash
.venv/bin/pip install pytest   # already in requirements.txt
.venv/bin/python -m pytest tests/ -v
```

`tests/test_db_smoke.py` runs the full pipeline against the real database
(scoped to the smallest clinic) and is skipped automatically if the DB file
is absent. Every other test uses small synthetic fixtures, no real data.

## Known limitations / open issues (see `IMPLEMENTATION_TRACEABILITY.md`)

- QC2 (narrow Set C, billing item C005-2) uses a candidate match string that
  is **not yet verified** against real `medication_name` values
  (OPEN-04-01) — any match is reported as `UNCONFIRMED`, never `Y`.
- QC1 (wide Set C) can only use the 2-digit `medical_class` (31/32/33); it
  cannot be split into D4-1's P01-P11 sub-categories because that DB column
  mapping is unverified (OPEN-04-02).
- `disease_code LIKE 'ZZZ%'` rows are flagged (`flag_zzz_pending_confirmation`)
  but never auto-classified — meaning is still unconfirmed (Session 02 #3).
- `perform_count` is exported raw and never interpreted as a count of actual
  administrations (Session 02 #4, still open).
- Day 0 / treatment episode / 30-day outcome are **never** computed by this
  tool — only ever entered by a human into the Manual Review / Outcome CSV
  templates outside this app.
- A 7th export, `12_supplementary_export.csv` (39 columns, added 2026-11-05,
  Block 7), runs **in parallel** with the 6 CSVs above per `document/A/
  AGRI_CARE_CSV_Design_Guide_v1.0.pdf` (REQ12) — it does not replace them.
  Most of its 20 "A" auto-extracted columns are always blank: either the
  data does not exist in the profiled database (age, sex, exact drug/
  infusion dates — `OUTSIDE_DATA`) or the aggregation/representative-row
  rule needed to compute them has not been approved yet (`UNDECIDED-S05-03
  ..10`, see `deliverables/session05/11_supplementary_csv_schema_mapping_vn.md`).
  Its `context_review_flags` column references `dictionaries/
  D5_context_flags.csv`, a DRAFT dictionary not yet reviewed against the
  Master Document like D1-D4. See `IMPLEMENTATION_TRACEABILITY.md` §8.
# -
