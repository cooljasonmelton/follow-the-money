# Follow The Money

Internal experiments tracking financial flows and related tooling.

## Agent OS Workflow

Check out [`AGENT_OS_HOWTO.md`](/docs/AGENT_OS_HOWTO.md) for the full command-by-command Agent OS playbook, including when to run `/plan-product`, `/shape-spec`, `/write-spec`, `/create-tasks`, `/implement-tasks`, and `/orchestrate-tasks`.

Keep the HOWTO handy inside Codex (e.g., `@learn AGENT_OS_HOWTO.md`) so every run follows the same process.

## Future Ideas

- Alerts for sudden donation spikes (notify analysts when contributions spike beyond historical norms)

## Local Development

1. Copy `.env.example` to `.env` and set `DATABASE_URL` and `OPENFEC_API_KEY`.
2. Install dependencies with `uv pip install -r pyproject.toml` (or standard pip).
3. Run historical ingest and normalization:
   ```bash
   make ingest-backfill
   make normalize
   make compute-leaning
   ```
4. Run validations and tests:
   ```bash
   pytest
   ```
See `docs/data/ingestion.md` for more detailed runbook steps.
