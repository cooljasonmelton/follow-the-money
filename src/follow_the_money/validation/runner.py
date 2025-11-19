from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from sqlalchemy import func, select
from sqlalchemy.engine import Engine

from follow_the_money.db import schema


class ValidationError(RuntimeError):
    pass


@dataclass
class ValidationRunner:
    engine: Engine
    row_count_tolerance: float = 0.05  # 5%

    def run(self, ingest_run_id: int) -> dict[str, int]:
        with self.engine.begin() as conn:
            staging_count = self._staging_row_count(conn, ingest_run_id)
            normalized_count = self._normalized_row_count(conn)
            if normalized_count == 0:
                raise ValidationError("Normalized rows missing; run normalization first.")
            tolerance = staging_count * self.row_count_tolerance
            if abs(normalized_count - staging_count) > tolerance:
                raise ValidationError(
                    f"Normalized rows ({normalized_count}) drift beyond tolerance from staging ({staging_count})."
                )
            total_amounts = self._total_amount_by_candidate(conn)
            for candidate_id, amount in total_amounts:
                if amount < 0:
                    raise ValidationError(f"Candidate {candidate_id} has negative aggregated contributions.")
            self._record_audit(conn, ingest_run_id, staging_count, normalized_count)
        return {"staging_rows": staging_count, "normalized_rows": normalized_count}

    def _staging_row_count(self, conn, ingest_run_id: int) -> int:
        tables = [
            schema.stg_fec_receipts,
            schema.stg_fec_committees,
            schema.stg_fec_candidates,
            schema.stg_fec_individual_contributions,
        ]
        total = 0
        for table in tables:
            total += conn.execute(
                select(func.count()).where(table.c.ingest_run_id == ingest_run_id)
            ).scalar() or 0
        return total

    def _normalized_row_count(self, conn) -> int:
        tables = [
            schema.candidates,
            schema.committees,
            schema.employers,
            schema.industries,
            schema.contributions,
        ]
        total = 0
        for table in tables:
            total += conn.execute(select(func.count()).select_from(table)).scalar() or 0
        return total

    def _total_amount_by_candidate(self, conn) -> Iterable[tuple[int, float]]:
        contributions = schema.contributions
        stmt = (
            select(contributions.c.candidate_id, func.sum(contributions.c.amount))
            .group_by(contributions.c.candidate_id)
        )
        return conn.execute(stmt).all()

    def _record_audit(self, conn, ingest_run_id: int, staging_count: int, normalized_count: int) -> None:
        conn.execute(
            schema.ingest_run_audits.update()
            .where(schema.ingest_run_audits.c.id == ingest_run_id)
            .values(
                warnings=[],
                rows_processed=normalized_count,
                status="validated",
            )
        )
