# Follow The Money

Internal experiments tracking financial flows and related tooling.

## Agent OS Workflow

Check out [`AGENT_OS_HOWTO.md`](/docs/AGENT_OS_HOWTO.md) for the full command-by-command Agent OS playbook, including when to run `/plan-product`, `/shape-spec`, `/write-spec`, `/create-tasks`, `/implement-tasks`, and `/orchestrate-tasks`.

Keep the HOWTO handy inside Codex (e.g., `@learn AGENT_OS_HOWTO.md`) so every run follows the same process.

## Future Ideas

- Alerts for sudden donation spikes (notify analysts when contributions spike beyond historical norms)

## Local Development

1. Copy `.env.example` to `.env` and set `DATABASE_URL`, `OPENFEC_API_KEY`, and `RAW_DATA_DIR` (defaults to `./data/raw`).
2. Create a virtual environment and install the project:
   ```bash
   uv venv              # or python3 -m venv .venv
   source .venv/bin/activate
   pip install -e .[dev]
   ```
3. Run historical ingest and normalization (large ZIP downloads ~4‑5 GB each; ensure at least 10 GB free). You can override the cycle with `CYCLE=2024` etc.:
   ```bash
   make ingest-backfill CYCLE=2024
   make normalize
   make compute-leaning
   ```
4. Run validations and tests:
   ```bash
   pytest
   ```
See `docs/data/ingestion.md` for more detailed runbook steps.
