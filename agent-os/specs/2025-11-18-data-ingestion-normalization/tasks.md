# Task Breakdown: Data Ingestion + Normalization

## Overview
Total Tasks: 19

## Task List

### Database & Storage Foundations

#### Task Group 1: Schema & migrations
**Dependencies:** None

- [ ] 1.0 Design and migrate core tables
  - [ ] 1.1 Draft ERD/schema plan covering staging tables, normalized fact/dim tables, reference lookups, audit logs
  - [ ] 1.2 Create migrations for staging tables (per source payload) with JSONB/raw columns + metadata
  - [ ] 1.3 Create migrations for normalized candidate/committee/employer/industry/contribution tables with surrogate keys + FK relationships
  - [ ] 1.4 Add indexes and partitioning strategy (quarter/year) for large fact tables
  - [ ] 1.5 Add `ingest_run_audits` table to track each ETL execution
  - [ ] 1.6 Write 2-4 focused schema tests (e.g., Alembic doctests or pytest migration checks) to verify constraints/indexes exist
  - [ ] 1.7 Run ONLY the schema tests from 1.6 to confirm migrations are valid

**Acceptance Criteria**
- All migrations run cleanly on fresh DB
- Keys/constraints enforce integrity between staging and normalized layers
- Schema tests pass

### Source Connectors & Raw Ingestion

#### Task Group 2: Source downloaders
**Dependencies:** Task Group 1

- [ ] 2.0 Implement data fetch layer
  - [ ] 2.1 Author reusable HTTP/download helpers with retries, checksum recording, and metadata logging
  - [ ] 2.2 Build FEC bulk downloader (historical + delta) storing raw files locally/S3
  - [ ] 2.3 Build OpenFEC API client with pagination + rate-limit handling
  - [ ] 2.4 Write 2-6 focused tests (pytest + pytest-vcr) covering each connector’s happy-path + failure handling
  - [ ] 2.5 Run ONLY the tests from 2.4

**Acceptance Criteria**
- Both connectors can fetch sample data and record metadata
- Tests verify retries/checksums/metadata and pass

#### Task Group 3: Raw staging load
**Dependencies:** Task Group 2

- [ ] 3.0 Persist downloaded data
  - [ ] 3.1 Implement parsers to read FEC bulk files into structured batches
  - [ ] 3.2 Load raw batches into staging tables with source identifiers + timestamps
  - [ ] 3.3 Log row counts, checksums, and payload windows per batch into `ingest_run_audits`
  - [ ] 3.4 Write 2-6 tests confirming raw loads preserve payload fidelity and metadata
  - [ ] 3.5 Run ONLY the tests from 3.4

**Acceptance Criteria**
- Staging tables contain exact source payloads
- Audit logs reflect each load
- Tests confirm fidelity and pass

### Normalization & Leaning Scores

#### Task Group 4: Normalization pipelines
**Dependencies:** Task Group 3

- [ ] 4.0 Transform staging data into normalized tables
  - [ ] 4.1 Implement mapping utilities for employers→industries (NAICS lookup) and committee/candidate relationships
  - [ ] 4.2 Create transformation scripts to populate candidate/committee/employer/industry/contribution tables with surrogate keys
  - [ ] 4.3 Ensure upserts handle corrections, dedupe logic, and maintain history snapshots as needed
  - [ ] 4.4 Write 2-6 tests verifying key relationships, dedup logic, and reference mappings
  - [ ] 4.5 Run ONLY the tests from 4.4

**Acceptance Criteria**
- Normalized tables populated with clean keys + FKs
- Mapping logic documented and tested

#### Task Group 5: Leaning score engine
**Dependencies:** Task Group 4

- [ ] 5.0 Compute 0–1 leaning scores
  - [ ] 5.1 Document scoring methodology in `docs/data/leaning-score.md`
  - [ ] 5.2 Implement score computation over rolling two-year window with configurable lookback
  - [ ] 5.3 Store scores with validity ranges and link to candidate/committee/employer/industry tables
  - [ ] 5.4 Write 2-6 tests that check deterministic scoring outputs for controlled inputs
  - [ ] 5.5 Run ONLY the tests from 5.4

**Acceptance Criteria**
- Scores computed for all entities with reproducible outputs
- Documentation explains formula and tie-breakers

### Orchestration & Tooling

#### Task Group 6: ETL scripts + runner
**Dependencies:** Task Groups 2-5

- [ ] 6.0 Provide scriptable ingestion workflow
  - [ ] 6.1 Build Python CLI scripts for `backfill`, `ingest-daily`, and `replay-range`
  - [ ] 6.2 Add Makefile targets (`make ingest-backfill`, `make ingest-daily`, etc.)
  - [ ] 6.3 Implement logging to stdout + `logs/ingest/YYYY-MM-DD.json`
  - [ ] 6.4 Write 2-4 tests for CLI orchestration (e.g., click/invoke unit tests or smoke tests with fixtures)
  - [ ] 6.5 Run ONLY the tests from 6.4

**Acceptance Criteria**
- Engineers can run one command to backfill or refresh data
- Logs show success/failure per run

#### Task Group 7: Validation & monitoring
**Dependencies:** Task Group 3+

- [ ] 7.0 Enforce validations
  - [ ] 7.1 Implement schema + aggregate validation routines (row counts, dollar sums) with configurable tolerances
  - [ ] 7.2 Fail runs and raise alerts/logs when tolerances exceeded
  - [ ] 7.3 Persist validation results to `ingest_run_audits`
  - [ ] 7.4 Write 2-6 tests covering pass/fail scenarios
  - [ ] 7.5 Run ONLY the tests from 7.4

**Acceptance Criteria**
- Each run produces a validation summary
- Failures block downstream steps and are logged

### Developer Enablement

#### Task Group 8: Docs & onboarding
**Dependencies:** Task Group 6

- [ ] 8.0 Document and polish developer experience
  - [ ] 8.1 Create `.env.example` with required env vars and usage notes
  - [ ] 8.2 Write `docs/data/ingestion.md` describing setup, commands, troubleshooting, and expected runtimes
  - [ ] 8.3 Update README “Future Ideas” section if new ideas emerged during build
  - [ ] 8.4 Record a short runbook snippet (e.g., in `docs/runbooks/ingest.md`) detailing how to rerun failed dates
  - [ ] 8.5 No tests required; review for clarity with another teammate if possible

**Acceptance Criteria**
- New contributors can follow docs to run backfill/daily flows locally
- Env setup instructions are complete
