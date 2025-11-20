# Ingest Runbook (Detailed)

## Environments
- **Local dev:** sqlite/postgres, run via CLI + Make targets
- **CI/CD:** future step—hook CLI commands into pipeline

## Routine
1. `make ingest-backfill` – fetch historical data (defaults to 2024; edit Makefile or pass `CYCLE` variable)
2. `make normalize` – transform staging payloads into normalized tables
3. `make compute-leaning` – recompute leaning scores
4. Validation:
   ```bash
   python - <<'PY'
   from sqlalchemy import create_engine
   from follow_the_money.validation import ValidationRunner
   engine = create_engine("postgresql+psycopg2://postgres:postgres@localhost:5432/follow_the_money")
   ValidationRunner(engine).run(ingest_run_id=YOUR_RUN_ID)
   PY
   ```
5. Monitor `agent-os/specs/<spec>/implementation/` for run logs (future step)

## Log locations
- STDOUT logging for CLI commands
- Plan to add JSON logs under `logs/ingest/YYYY-MM-DD.json`
