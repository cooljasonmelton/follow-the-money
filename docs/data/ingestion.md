# Ingestion Runbook

## Prerequisites
- `.env` configured with `DATABASE_URL`, `OPENFEC_API_KEY`, and `RAW_DATA_DIR`
- Dockerized Postgres running locally (`docker compose up db`)
- Python 3.11 env with dependencies (`uv pip install -r pyproject.toml`)

## Commands

Global options: `DATABASE_URL` can be overridden per command:

```bash
make ingest-backfill DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/ftm
```

### Backfill
```bash
make ingest-backfill CYCLE=2024
```
Downloads historical receipts for the configured cycles (defaults to 2024 via `CYCLE`). The FEC “all individual contributions” ZIP is ~4–5 GB, so plan for at least 10 GB free before unzipping. Progress is logged before/after every download.

### Daily ingest
```bash
make ingest-daily CYCLE=2026
```
Runs the same flow for a single cycle.

### Normalize
```bash
make normalize
```
Transforms staging data (latest run) into normalized tables.

### Compute leaning
```bash
make compute-leaning
```
Calculates leaning scores for the latest window and stores them in `leaning_scores`.

### Validation
Invoke validation via Python (future CLI flag to be added):

```bash
python -c "from follow_the_money.validation import ValidationRunner; from sqlalchemy import create_engine; eng=create_engine('DATABASE_URL'); ValidationRunner(eng).run(ingest_run_id)"
```

## Troubleshooting

- **Missing run**: `ValidationRunner`/normalize commands require at least one ingest run ID; ensure ingest commands were executed first.
- **checksum mismatch**: remove partial ZIPs in `data/raw/` and rerun ingest.
- **pytest fails**: install dev deps offline by pulling wheels ahead of time or run in an environment with internet access.
- **Huge downloads**: if disk space is low, remove `data/raw/*.zip` after ingestion, or point `RAW_DATA_DIR` to an external drive.
- **Recovering from hangs**: downloads can take several minutes; press `Ctrl+C` to abort and rerun once you have bandwidth/disk space. The CLI now logs when a download starts and finishes so you can tell whether it’s progressing.
