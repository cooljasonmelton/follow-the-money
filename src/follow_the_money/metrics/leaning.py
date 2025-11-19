from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import delete, func, insert, literal, select
from sqlalchemy.engine import Engine

from follow_the_money.db import schema


PARTY_LEFT = {"DEM", "D", "DEMCRATIC", "DEMCRAT"}
PARTY_RIGHT = {"REP", "R", "REPUBLICAN", "GOP"}


@dataclass(slots=True)
class LeaningScoreCalculator:
    engine: Engine
    lookback_days: int = 730
    min_sample_size: int = 5
    methodology_version: str = "v1"

    def run(self, *, as_of: date | None = None) -> None:
        today = as_of or datetime.now(timezone.utc).date()
        window_start = today - timedelta(days=self.lookback_days)
        window_end = today
        contributions = schema.contributions

        with self.engine.begin() as conn:
            left_committee_ids, right_committee_ids = self._committee_party_sets(conn)
            window_stmt = select(contributions).where(
                contributions.c.transaction_dt >= window_start,
                contributions.c.transaction_dt <= window_end,
            )
            rows = conn.execute(window_stmt).mappings().all()

            aggregates = defaultdict(lambda: {"left": Decimal("0"), "right": Decimal("0"), "count": 0})
            for row in rows:
                entity_candidates = [
                    ("candidate", row["candidate_id"]),
                    ("committee", row["committee_id"]),
                    ("employer", row["employer_id"]),
                    ("industry", row["industry_id"]),
                ]
                committee_id = row["committee_id"]
                amount = Decimal(row["amount"] or "0")
                is_left = committee_id in left_committee_ids
                is_right = committee_id in right_committee_ids
                for entity_type, entity_id in entity_candidates:
                    if not entity_id:
                        continue
                    bucket = aggregates[(entity_type, entity_id)]
                    if is_left:
                        bucket["left"] += amount
                    if is_right:
                        bucket["right"] += amount
                    bucket["count"] += 1

            score_rows = []
            for (entity_type, entity_id), bucket in aggregates.items():
                left = bucket["left"]
                right = bucket["right"]
                total = left + right
                score = right / total if total > 0 else Decimal("0.5")
                score_rows.append(
                    {
                        "entity_type": entity_type,
                        "entity_id": entity_id,
                        "score": round(score, 3),
                        "left_amount": round(left, 2),
                        "right_amount": round(right, 2),
                        "sample_size": bucket["count"],
                        "window_start": window_start,
                        "window_end": window_end,
                        "computed_at": datetime.now(timezone.utc),
                        "methodology_version": self.methodology_version,
                        "created_at": datetime.now(timezone.utc),
                    }
                )

            conn.execute(
                delete(schema.leaning_scores).where(
                    schema.leaning_scores.c.window_start == window_start,
                    schema.leaning_scores.c.window_end == window_end,
                    schema.leaning_scores.c.methodology_version == self.methodology_version,
                )
            )

            if score_rows:
                conn.execute(insert(schema.leaning_scores), score_rows)

    def _committee_party_sets(self, conn) -> tuple[set[int], set[int]]:
        committees = schema.committees
        rows = conn.execute(select(committees.c.id, committees.c.party)).fetchall()
        left = {row.id for row in rows if row.party and row.party.upper() in PARTY_LEFT}
        right = {row.id for row in rows if row.party and row.party.upper() in PARTY_RIGHT}
        return left, right
