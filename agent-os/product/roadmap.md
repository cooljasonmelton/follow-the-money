# Product Roadmap

## Backend & Data

1. [x] Data ingestion + normalization — Stand up ETL to pull FEC filings, PAC rosters, employer metadata, and normalize everything into a Postgres schema with leaning scores for candidates, committees, employers, and industries. `L`
2. [ ] Messaging vs funding alignment module — Ship NLP pipeline (spaCy/scikit-learn) to extract messaging themes from press releases, correlate them with funding sources, and surface alignment/contradiction scores in the API. `L`
3. [ ] Follow-the-money graph API — Build services that expose entity relationships, weighted donations, and filters for the graph explorer, including caching for large traversals. `L`

## API Layer

4. [ ] Candidate funding breakdown endpoints — Provide REST/GraphQL endpoints that summarize donation mix by leaning, industry, and top employers, including pagination and export-ready responses. `M`
5. [ ] Employer & industry explorer endpoints — Deliver APIs for party split percentages, trend charts, and top-supported candidates over time with consistent query params for the frontend. `M`
6. [ ] Advanced filtering & bookmarking APIs — Support global filters (time range, geography, entity type) plus CRUD for saved views/bookmarks so researchers can persist their settings. `M`

## Frontend Experience

7. [ ] Candidate funding breakdown dashboard — Build UI cards/tables that consume the candidate endpoints, highlight mix percentages, and offer CSV/PNG exports. `M`
8. [ ] Employer & industry explorer UI — Create interactive charts for employer/industry party splits, trend lines, and top candidates, reusing shared components. `M`
9. [ ] Follow-the-money graph explorer — Implement PyVis/Sigma-based visualization with entity filters, donation threshold slider, and leaning-based color scales. `L`
10. [ ] Advanced filtering & bookmarking UI — Add global filter controls, saved-view management, and quick toggles so users can switch between perspectives effortlessly. `M`

## Collaboration & Launch Readiness

11. [ ] Collaboration and sharing toolkit — Provide embeddable snippets, CSV/PNG exports, and shareable links so journalists and watchdog groups can distribute insights quickly. `M`
12. [ ] Public transparency portal polish — Harden authentication, add onboarding walkthroughs, improve accessibility, and publish documentation that reinforces the nonpartisan mission ahead of broader launch. `M`

> Notes
> - Backend data work (items 1–3) is prerequisite for both API and frontend layers.
> - API work (items 4–6) feeds the frontend slices (items 7–10) so each UI feature has complete data coverage.
> - Collaboration & launch tasks (items 11–12) sit at the end to polish before public access.
