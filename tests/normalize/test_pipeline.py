from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import create_engine, select

from follow_the_money.db import schema
from follow_the_money.ingest.staging_loader import StagingLoader
from follow_the_money.normalize import NormalizationPipeline
from follow_the_money.sources.types import SourceMetadata


def make_metadata() -> SourceMetadata:
    now = datetime.now(timezone.utc)
    return SourceMetadata(
        url="https://example.com",
        status_code=200,
        headers={},
        params=None,
        bytes_written=0,
        checksum="abc",
        requested_at=now,
        completed_at=now,
    )


def test_pipeline_normalizes_entities(tmp_path: Path) -> None:
    engine = create_engine("sqlite:///:memory:")
    schema.metadata.create_all(engine)
    loader = StagingLoader(engine)
    pipeline = NormalizationPipeline(engine)

    metadata = make_metadata()
    run_id = loader.start_run(run_key="test-run", source="bulk", metadata=metadata)

    loader.load_raw_records(
        "stg_fec_candidates",
        records=[
            {"fec_id": "C123", "first_name": "Ann", "last_name": "Example", "party": "DEM"},
        ],
        ingest_run_id=run_id,
        source_file="candidates.txt",
    )

    loader.load_raw_records(
        "stg_fec_committees",
        records=[
            {"fec_id": "CM321", "name": "Friends of Ann"},
        ],
        ingest_run_id=run_id,
        source_file="committees.txt",
    )

    loader.load_raw_records(
        "stg_fec_receipts",
        records=[
            {
                "fec_record_id": "TX001",
                "cand_id": "C123",
                "committee_id": "CM321",
                "amount": "1500",
                "transaction_dt": "2024-02-01",
                "cycle": "2024",
                "employer": "Acme Technologies",
                "occupation": "Software Engineer",
                "receipt_type": "PAC",
            },
            {
                "fec_record_id": "TX002",
                "cand_id": "C123",
                "committee_id": "CM321",
                "amount": "2000",
                "transaction_dt": "2024-03-01",
                "cycle": "2024",
                "employer": "ACME TECHNOLOGIES INC",
                "occupation": "Developer",
                "receipt_type": "PAC",
            },
        ],
        ingest_run_id=run_id,
        source_file="receipts.txt",
    )

    pipeline.run(run_id)

    with engine.begin() as conn:
        candidates = conn.execute(select(schema.candidates)).fetchall()
        committees = conn.execute(select(schema.committees)).fetchall()
        links = conn.execute(select(schema.committee_candidate_links)).fetchall()
        employers = conn.execute(select(schema.employers)).fetchall()
        industries = conn.execute(select(schema.industries)).fetchall()
        employer_industries = conn.execute(select(schema.employer_industries)).fetchall()
        contributions = conn.execute(select(schema.contributions)).fetchall()

    assert len(candidates) == 1
    assert candidates[0].fec_id == "C123"
    assert len(committees) == 1
    assert len(links) == 1

    assert len(employers) == 1
    assert employers[0].normalized_name == "ACME TECHNOLOGIES"

    assert len(industries) == 1
    assert industries[0].code == "TECH"
    assert len(employer_industries) == 1
    assert employer_industries[0].employer_id == employers[0].id

    assert len(contributions) == 2
    assert contributions[0].candidate_id == candidates[0].id
