# Leaning Score Methodology

We compute a 0–1 leaning score for each entity (candidate, committee, employer, industry) based on donation flows observed over a rolling two-year window.

## Formula

Let:
- `L` = total inflows attributed to left-leaning committees/candidates for the entity in the window
- `R` = total inflows attributed to right-leaning committees/candidates for the entity in the window

Score = `R / (L + R)` when `(L + R) > 0`, otherwise default to 0.5.

- Resulting score ranges from 0.0 (solidly left donations) to 1.0 (solidly right).
- Entities with insufficient sample size (< 5 transactions by default) are stored but flagged via `sample_size`.

## Steps
1. Derive left/right classification for each committee/candidate based on party.
2. Aggregate contribution amounts per entity -> {left_total, right_total, sample_size}.
3. Compute the score using the formula and store `window_start`, `window_end`, `methodology_version`.
4. Scores are upserted per window (unique constraint ensures only one record per entity/window).
