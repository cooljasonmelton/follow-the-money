# Specification: Data Ingestion + Normalization

## Goal
Build the first iteration of the Follow the Money data backbone by ingesting FEC bulk filings and OpenFEC APIs, persisting both raw and normalized datasets in Postgres, and computing transparent leaning scores that downstream APIs and dashboards can trust.

## User Stories
- As a data engineer, I need an automated pipeline that ingests campaign-finance data daily so analysts always work from fresh, consistent facts.
- As a civic researcher, I want candidate, PAC, employer, and industry records to include a leaning score so I can compare funding patterns without manual math.
- As a journalist, I need confidence that donation totals match official filings so I can cite the platform as a reliable source.

## Specific Requirements

**Source connectors**
- Pull historical and daily updates from FEC bulk data dumps (receipts, committees, candidates, individual contributions).
- Call OpenFEC API endpoints to enrich entities with metadata not present in the bulk files.
- Store source metadata (download timestamp, endpoint URL, request parameters, version hashes) for auditability.

**Raw staging layer**
- Persist exact source payloads in Postgres staging tables (JSONB or denormalized wide tables) keyed by source file + record ID.
- Include ingestion logs (row counts, checksums, data window) per run.
- Never mutate these tables except to append or mark deleted when upstream publishes corrections.

**Normalization & reference tables**
- Create normalized fact/dimension tables for candidates, committees/PACs, employers, industries, and contributions with stable surrogate keys.
- Derive employer + industry mappings (e.g., via NAICS lookup) and keep reference tables versioned.
- Ensure relationships (candidate↔committee, employer↔industry) have foreign keys and indexes for downstream joins.

**Leaning score computation**
- Define a 0–1 leaning score where 0.0 is solidly left-leaning donations and 1.0 is solidly right-leaning, computed as ratio of donations to each side over a rolling two-year window.
- Document the formula, data windows, and tie-breaking rules inside the repo (e.g., `docs/data/leaning-score.md`) so analysts understand the methodology.
- Store computed scores with timestamped validity periods to enable historical comparisons.

**Ingestion cadence & orchestration**
- Provide Python scripts (no Prefect for MVP) that support: initial backfill, daily incremental ingest, and manual re-run of a given date range.
- Wire scripts to a Makefile or lightweight runner so CI/cron jobs can invoke `make ingest-backfill`, `make ingest-daily`, etc.
- Log to stdout + JSON files under `logs/ingest/YYYY-MM-DD.json` for observability.

**Validation & monitoring**
- Implement schema validation (field presence, types) and aggregate sanity checks (row counts vs upstream totals, checksum of dollar amounts) per run.
- Fail the run if discrepancies exceed configurable tolerances; emit a summary report (counts, timestamps, warnings).
- Record validation outcomes in a `ingest_run_audits` table for inspection.

**Performance & storage management**
- Partition large fact tables by filing quarter or year to keep queries performant.
- Add indexes on common filter columns (candidate_id, committee_id, employer_id, filing_period).
- Define pruning/archival strategy for raw staging data if storage thresholds are hit (e.g., keep 3 years locally, archive older payloads to S3).

**Developer ergonomics**
- Provide sample `.env.example` with required FEC/OpenFEC credentials or rate-limit keys.
- Document how to bootstrap a local Postgres instance (e.g., `docker compose up db`) and run `make ingest-backfill` end-to-end.
- Include troubleshooting section for common failures (API limits, malformed files, network retries).

## Visual Design
No visuals provided for this backend-focused spec.

## Existing Code to Leverage
- None identified yet; this is the initial ingestion subsystem. Future specs should reference these tables and scripts once implemented.

## Out of Scope
- Prefect or other heavy orchestration frameworks (will revisit after MVP).
- Real-time streaming/webhook ingestion (daily batch only for now).
- Alerts for sudden donation spikes (tracked in README future ideas).
- Downstream APIs, dashboards, or graph visualizations (covered by later roadmap items).
- Non-FEC or international data sources.
