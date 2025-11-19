# Data Ingestion Schema Plan

## Staging Layer
- `stg_fec_receipts`, `stg_fec_committees`, `stg_fec_candidates`, `stg_fec_individual_contributions`
  - Store raw payloads from their respective FEC bulk downloads/OpenFEC responses
  - Common columns: `ingest_run_id`, `source_file`, `payload_hash`, `payload JSON`, `filing_date`, `cycle`, timestamps
  - Maintain immutability—only append or mark records superseded via ingest metadata

## Normalized Entities
- `candidates`: canonical record per FEC candidate ID, includes party/office metadata and raw source context
- `committees`: canonical PAC/committee record plus type/party/designation
- `committee_candidate_links`: maintain many-to-many relationships between committees and the candidates they support
- `employers`: deduplicated employer entities with normalized names and optional geography
- `industries`: industry taxonomy (NAICS/Sector) and `employer_industries` link table with confidence weighting
- `contributions`: fact table linking candidate, committee, employer, and industry plus transaction details
- `leaning_scores`: 0–1 scores per entity per rolling window capturing ratios of left/right donations

## Audit & Validation
- `ingest_run_audits`: log each ETL execution with run key, timestamps, row counts, checksums, and warning/error payloads
- Validation routines record pass/fail in this table and all staging rows reference the run that produced them

## Partitioning & Indexing
- Partition `contributions` by filing quarter (RANGE on `transaction_dt`) to keep query costs predictable
- Add indexes on `(candidate_id, cycle)`, `(committee_id, cycle)`, `(employer_id, cycle)` plus surrogate key lookups to support dashboards
- Reference tables (`employers`, `industries`) enforce uniqueness on identifiers (hash or code) to simplify upserts
