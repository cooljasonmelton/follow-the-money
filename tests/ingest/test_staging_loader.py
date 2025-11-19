from __future__ import annotations

import zipfile
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import create_engine, select

from follow_the_money.db import schema
from follow_the_money.ingest import iter_zip_tsv
from follow_the_money.ingest.staging_loader import StagingLoader
from follow_the_money.sources.types import SourceMetadata


def make_metadata() -> SourceMetadata:
    now = datetime.now(timezone.utc)
    return SourceMetadata(
        url="https://example.com/file.zip",
        status_code=200,
        headers={"Content-Length": "10"},
        params=None,
        bytes_written=10,
        checksum="abc123",
        requested_at=now,
        completed_at=now,
    )


def test_staging_loader_inserts_rows(tmp_path: Path) -> None:
    engine = create_engine("sqlite:///:memory:")
    schema.metadata.create_all(engine)
    loader = StagingLoader(engine)

    metadata = make_metadata()
    run_id = loader.start_run(run_key="test-run", source="fec-indiv", metadata=metadata)

    records = [
        {"id": "1", "amount": "100", "cycle": "2024", "filing_date": "2024-01-01"},
        {"id": "2", "amount": "200", "cycle": "2024", "filing_date": "2024-01-02"},
    ]
    inserted = loader.load_raw_records(
        "stg_fec_receipts",
        records=records,
        ingest_run_id=run_id,
        source_file="2024indiv.zip",
    )
    assert inserted == 2

    loader.complete_run(run_id, status="succeeded", rows_processed=inserted)

    with engine.begin() as conn:
        table = schema.metadata.tables["stg_fec_receipts"]
        rows = conn.execute(select(table)).fetchall()
        assert len(rows) == 2
        assert rows[0].payload["amount"] == "100"

        audit = conn.execute(
            select(schema.ingest_run_audits).where(schema.ingest_run_audits.c.id == run_id)
        ).one()
        assert audit.rows_processed == 2
        assert audit.status == "succeeded"
