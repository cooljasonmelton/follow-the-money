from __future__ import annotations

import pytest
from datetime import datetime, timezone, date
from uuid import uuid4

from sqlalchemy import create_engine, insert

from follow_the_money.db import schema
from follow_the_money.validation import ValidationRunner, ValidationError


@pytest.fixture()
def engine():
    engine = create_engine("sqlite:///:memory:")
    schema.metadata.create_all(engine)
    return engine


def seed_data(engine, ingest_run_id: int):
    now = datetime.now(timezone.utc)
    with engine.begin() as conn:
        conn.execute(
            schema.candidates.insert(),
            [
                {"fec_id": "C1", "first_name": "A", "last_name": "B", "created_at": now, "updated_at": now},
            ],
        )
        conn.execute(
            schema.committees.insert(),
            [
                {"fec_id": "L1", "name": "Left", "party": "DEM", "created_at": now, "updated_at": now},
            ],
        )
        conn.execute(
            schema.employers.insert(),
            [
                {"name": "ACME", "normalized_name": "ACME", "employer_hash": "hash", "created_at": now, "updated_at": now},
            ],
        )
        conn.execute(
            schema.contributions.insert(),
            [
                {
                    "fec_record_id": "TX1",
                    "candidate_id": 1,
                    "committee_id": 1,
                    "amount": 10,
                    "transaction_dt": date.today(),
                    "cycle": "2024",
                    "is_individual": True,
                    "created_at": now,
                    "updated_at": now,
                }
            ],
        )
        conn.execute(
            schema.stg_fec_receipts.insert(),
            [
                {
                    "ingest_run_id": ingest_run_id,
                    "source_file": "file",
                    "payload_hash": "hash1",
                    "payload": {},
                    "cycle": "2024",
                    "filing_date": date.today(),
                    "received_at": now,
                    "created_at": now,
                    "updated_at": now,
                },
                {
                    "ingest_run_id": ingest_run_id,
                    "source_file": "file2",
                    "payload_hash": "hash2",
                    "payload": {},
                    "cycle": "2024",
                    "filing_date": date.today(),
                    "received_at": now,
                    "created_at": now,
                    "updated_at": now,
                },
            ],
        )


def test_validation_runner_passes(engine):
    now = datetime.now(timezone.utc)
    with engine.begin() as conn:
        run_id = conn.execute(
            schema.ingest_run_audits.insert().values(
                run_key="run1",
                source="test",
                status="running",
                started_at=now,
                rows_processed=0,
                checksum="abc",
                warnings=[],
                created_at=now,
                updated_at=now,
            )
        ).inserted_primary_key[0]
    seed_data(engine, run_id)
    runner = ValidationRunner(engine, row_count_tolerance=1.0)
    result = runner.run(run_id)
    assert result["normalized_rows"] >= 1


def test_validation_runner_fail_on_row_drift(engine):
    now = datetime.now(timezone.utc)
    with engine.begin() as conn:
        run_id = conn.execute(
            schema.ingest_run_audits.insert().values(
                run_key="run2",
                source="test",
                status="running",
                started_at=now,
                rows_processed=0,
                checksum="abc",
                warnings=[],
                created_at=now,
                updated_at=now,
            )
        ).inserted_primary_key[0]
        # no staging rows, but insert normalized data to trigger drift
        conn.execute(
            schema.candidates.insert(),
            [
                {"fec_id": "CNEG", "first_name": "Bad", "last_name": "Actor", "created_at": now, "updated_at": now},
            ],
        )
        conn.execute(
            schema.committees.insert(),
            [
                {"fec_id": "NEG", "name": "Neg PAC", "party": "REP", "created_at": now, "updated_at": now},
            ],
        )
        conn.execute(
            schema.contributions.insert(),
            [
                {
                    "fec_record_id": f"POS-{uuid4()}",
                    "candidate_id": 1,
                    "committee_id": 1,
                    "amount": 10,
                    "transaction_dt": date.today(),
                    "cycle": "2024",
                    "is_individual": True,
                    "created_at": now,
                    "updated_at": now,
                }
            ],
        )

    runner = ValidationRunner(engine, row_count_tolerance=0.1)
    with pytest.raises(ValidationError):
        runner.run(run_id)
