# Task Breakdown: Data Ingestion + Normalization

## Overview
Total Tasks: 19

## Task List

### Database & Storage Foundations

#### Task Group 1: Schema & migrations
**Dependencies:** None

- [x] 1.0 Design and migrate core tables
  - [x] 1.1 Draft ERD/schema plan covering staging tables, normalized fact/dim tables, reference lookups, audit logs
  - [x] 1.2 Create migrations for staging tables (per source payload) with JSONB/raw columns + metadata
  - [x] 1.3 Create migrations for normalized candidate/committee/employer/industry/contribution tables with surrogate keys + FK relationships
  - [x] 1.4 Add indexes and partitioning strategy (quarter/year) for large fact tables
  - [x] 1.5 Add `ingest_run_audits` table to track each ETL execution
  - [x] 1.6 Write 2-4 focused schema tests (e.g., Alembic doctests or pytest migration checks) to verify constraints/indexes exist
  - [x] 1.7 Run ONLY the schema tests from 1.6 to confirm migrations are valid

**Acceptance Criteria**
- All migrations run cleanly on fresh DB
- Keys/constraints enforce integrity between staging and normalized layers
- Schema tests pass

### Source Connectors & Raw Ingestion

#### Task Group 2: Source downloaders
**Dependencies:** Task Group 1

- [x] 2.0 Implement data fetch layer
  - [x] 2.1 Author reusable HTTP/download helpers with retries, checksum recording, and metadata logging
  - [x] 2.2 Build FEC bulk downloader (historical + delta) storing raw files locally/S3
  - [x] 2.3 Build OpenFEC API client with pagination + rate-limit handling
  - [x] 2.4 Write 2-6 focused tests (pytest) covering each connector’s happy-path + failure handling
  - [x] 2.5 Run ONLY the tests from 2.4

**Acceptance Criteria**
- Both connectors can fetch sample data and record metadata
- Tests verify retries/checksums/metadata and pass

#### Task Group 3: Raw staging load
**Dependencies:** Task Group 2

- [x] 3.0 Persist downloaded data
  - [x] 3.1 Implement parsers to read FEC bulk files into structured batches
  - [x] 3.2 Load raw batches into staging tables with source identifiers + timestamps
  - [x] 3.3 Log row counts, checksums, and payload windows per batch into `ingest_run_audits`
  - [x] 3.4 Write 2-6 tests confirming raw loads preserve payload fidelity and metadata
  - [x] 3.5 Run ONLY the tests from 3.4

**Acceptance Criteria**
- Staging tables contain exact source payloads
- Audit logs reflect each load
- Tests confirm fidelity and pass

### Normalization & Leaning Scores

#### Task Group 4: Normalization pipelines
**Dependencies:** Task Group 3

- [x] 4.0 Transform staging data into normalized tables
  - [x] 4.1 Implement mapping utilities for employers→industries (NAICS lookup) and committee/candidate relationships
  - [x] 4.2 Create transformation scripts to populate candidate/committee/employer/industry/contribution tables with surrogate keys
  - [x] 4.3 Ensure upserts handle corrections, dedupe logic, and maintain history snapshots as needed
  - [x] 4.4 Write 2-6 tests verifying key relationships, dedup logic, and reference mappings
  - [x] 4.5 Run ONLY the tests from 4.4

**Acceptance Criteria**
- Normalized tables populated with clean keys + FKs
- Mapping logic documented and tested

#### Task Group 5: Leaning score engine
**Dependencies:** Task Group 4

- [x] 5.0 Compute 0–1 leaning scores
  - [x] 5.1 Document scoring methodology in `docs/data/leaning-score.md`
  - [x] 5.2 Implement score computation over rolling two-year window with configurable lookback
  - [x] 5.3 Store scores with validity ranges and link to candidate/committee/employer/industry tables
  - [x] 5.4 Write 2-6 tests that check deterministic scoring outputs for controlled inputs
  - [x] 5.5 Run ONLY the tests from 5.4

**Acceptance Criteria**
- Scores computed for all entities with reproducible outputs
- Documentation explains formula and tie-breakers

### Orchestration & Tooling

#### Task Group 6: ETL scripts + runner
**Dependencies:** Task Groups 2-5

- [x] 6.0 Provide scriptable ingestion workflow
  - [x] 6.1 Build Python CLI scripts for `backfill`, `ingest-daily`, and `replay-range`
  - [x] 6.2 Add Makefile targets (`make ingest-backfill`, `make ingest-daily`, etc.)
  - [x] 6.3 Implement logging to stdout + `logs/ingest/YYYY-MM-DD.json`
  - [x] 6.4 Write 2-4 tests for CLI orchestration (e.g., click/invoke unit tests or smoke tests with fixtures)
  - [x] 6.5 Run ONLY the tests from 6.4

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
