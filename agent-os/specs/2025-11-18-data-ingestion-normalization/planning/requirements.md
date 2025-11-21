# Spec Requirements: Data Ingestion + Normalization

## Initial Description
Data ingestion + normalization — Stand up ETL to pull FEC filings, PAC rosters, employer metadata, and normalize everything into a Postgres schema with leaning scores for candidates, committees, employers, and industries.

## Requirements Discussion

### First Round Questions

**Q1:** I’m assuming we’ll ingest FEC bulk filings plus OpenSecrets-style PAC/employer reference data. Is that correct, or do you have additional sources (e.g., TransparencyData snapshots, custom scrapers) that must be included in this first pass?  
**Answer:** Use Federal Election Commission bulk data and the official OpenFEC API as the initial sources, then store the data in our own tables. Open to additional sources later.

**Q2:** I’m thinking of a nightly ETL cadence with incremental updates after the initial historical backfill. Should we plan for real-time hooks (webhooks/streaming) instead, or is daily refresh acceptable?  
**Answer:** Daily refresh is acceptable for MVP.

**Q3:** For leaning scores, I’d default to calculating ratios of donations to left/right entities over a rolling window. Do you already have a scoring rubric (e.g., 0–1 scale) we should replicate, or should this spec define a new methodology?  
**Answer:** No existing rubric—let’s adopt your suggested 0–1 methodology.

**Q4:** To keep audits clean, I’d like to store raw staging tables (exact source payloads) alongside normalized fact tables in Postgres. Are there compliance or storage constraints that would prevent us from retaining the raw feeds?  
**Answer:** None. We’re only using public APIs, so retaining raw payloads is fine.

**Q5:** Should we scope data validation to schema checks + aggregate sanity (row counts, checksum against source totals), or do you need deeper anomaly detection (e.g., sudden donation spikes triggering alerts) in this phase?  
**Answer:** Stick to schema + aggregate validations for MVP, but log “alerts for sudden donation spikes” as a future feature idea.

**Q6:** Do you want the ETL orchestration handled entirely inside Prefect flows (as per our tech stack), or should we integrate with any existing job scheduler / observability tooling?  
**Answer:** Skip Prefect for MVP—use Python scripts plus a lightweight runner/Makefile workflow instead.

**Q7:** Are there any jurisdictions, election cycles, or entity types that should be explicitly excluded from this initial ingestion?  
**Answer:** None—ingest everything available from the sources above.

### Existing Code to Reference
No similar existing features identified for reference.

### Follow-up Questions

**Follow-up 1:** On leaning scores, are you comfortable if we define a 0–1 spectrum by taking donation ratios over a rolling window and document that formula in the spec?  
**Answer:** Yes, go with that suggestion.

**Follow-up 2:** Where should we track future feature ideas like “alerts for sudden donation spikes”?  
**Answer:** Add a “Future Ideas” section at the bottom of the main README and record it there.

## Visual Assets

### Files Provided:
No visual files were found in `agent-os/specs/2025-11-18-data-ingestion-normalization/planning/visuals/`.
