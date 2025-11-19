# Tech Stack

## Runtime & Framework
- **Primary language:** Python 3.11 (data processing, backend services)
- **Backend framework:** FastAPI for API layer and service orchestration
- **Frontend framework:** Next.js / React with TypeScript for SPA-style dashboards
- **Package management:** `uv` for Python environments; `pnpm` for frontend dependencies

## Data & Storage
- **Database:** PostgreSQL (OLTP + analytics-ready schema)
- **ORM / query layer:** SQLAlchemy + Alembic for migrations; Pandas/Polars for analytical transforms
- **Cache / queue:** Redis (caching filters, precomputed graph traversals, async jobs)
- **Object storage:** S3-compatible bucket for press-release archives and export artifacts

## Data Processing & AI
- **ETL tooling:** Prefect flows containerized with Docker; scheduled via Prefect Cloud or self-hosted agent
- **NLP stack:** spaCy + scikit-learn (messaging topic extraction / alignment scores)
- **Graph modeling:** NetworkX for compute, surfaced via PyVis/Sigma environments

## Frontend Experience
- **UI components:** shadcn/ui + Tailwind CSS for consistent styling
- **Data viz libraries:** Recharts / D3 for charts; Sigma.js for graph explorer; Plotly for ad-hoc dashboards
- **State & caching:** React Query (TanStack Query) tied to FastAPI endpoints

## Testing & Quality
- **Python testing:** pytest + pytest-vcr for HTTP recording; `ruff` + `black` + `mypy` for lint/format/type
- **Frontend testing:** Vitest + Testing Library; Playwright for end-to-end flows
- **CI/CD:** GitHub Actions running lint/type/test suites and container builds

## Deployment & Infrastructure
- **Hosting:** Fly.io or Railway for the monorepo (FastAPI + Next.js) with Docker images
- **CDN / Edge:** Vercel Edge or Cloudflare for serving static assets quickly
- **Secrets management:** `.env` files + Doppler/1Password, loaded via Pydantic `BaseSettings`
- **Monitoring:** Sentry for app errors; Loguru + OpenTelemetry traces for backend observability

## Third-Party Integrations
- **Authentication:** Auth0 (passwordless + OAuth) with role-based access for journalists vs public users
- **Email / notifications:** Postmark transactional emails for saved reports / alerts
- **Data sources:** FEC APIs, OpenSecrets, TransparencyData snapshots, custom scrapers for press releases
