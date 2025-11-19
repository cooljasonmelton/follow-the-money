from __future__ import annotations

import json
from datetime import date, datetime, timezone
from hashlib import sha256
from typing import Iterable, Mapping

from sqlalchemy import insert, update
from sqlalchemy.engine import Engine

from follow_the_money.db import schema
from follow_the_money.sources.types import SourceMetadata


class StagingLoader:
    """Load raw records into staging tables while logging ingest runs."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def start_run(self, *, run_key: str, source: str, metadata: SourceMetadata) -> int:
        now = datetime.now(timezone.utc)
        stmt = insert(schema.ingest_run_audits).values(
            run_key=run_key,
            source=source,
            status="running",
            started_at=metadata.requested_at,
            completed_at=None,
            rows_processed=0,
            checksum=metadata.checksum,
            warnings=[],
            error_message=None,
            created_at=now,
            updated_at=now,
        )
        with self.engine.begin() as conn:
            result = conn.execute(stmt)
            run_id = result.inserted_primary_key[0]
        return int(run_id)

    def complete_run(
        self,
        run_id: int,
        *,
        status: str,
        rows_processed: int,
        warnings: list[str] | None = None,
        error_message: str | None = None,
        completed_at: datetime | None = None,
    ) -> None:
        stmt = (
            update(schema.ingest_run_audits)
            .where(schema.ingest_run_audits.c.id == run_id)
            .values(
                status=status,
                rows_processed=rows_processed,
                warnings=warnings or [],
                error_message=error_message,
                completed_at=completed_at or datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
        )
        with self.engine.begin() as conn:
            conn.execute(stmt)

    def load_raw_records(
        self,
        table_name: str,
        *,
        records: Iterable[Mapping[str, object]],
        ingest_run_id: int,
        source_file: str,
        default_cycle: str | None = None,
    ) -> int:
        table = schema.metadata.tables[table_name]
        received_at = datetime.now(timezone.utc)
        to_insert = []
        for record in records:
            payload = dict(record)
            cycle = payload.get("cycle") or default_cycle
            filing_date = payload.get("filing_date")
            if isinstance(filing_date, str):
                try:
                    filing_date = date.fromisoformat(filing_date)
                except ValueError:
                    filing_date = None
            serialized = json.dumps(payload, sort_keys=True, default=str)
            payload_hash = sha256(serialized.encode("utf-8")).hexdigest()
            to_insert.append(
                {
                    "ingest_run_id": ingest_run_id,
                    "source_file": source_file,
                    "payload_hash": payload_hash,
                    "payload": payload,
                    "cycle": cycle,
                    "filing_date": filing_date,
                    "received_at": received_at,
                    "created_at": received_at,
                    "updated_at": received_at,
                }
            )
        if not to_insert:
            return 0
        with self.engine.begin() as conn:
            conn.execute(insert(table), to_insert)
        return len(to_insert)
