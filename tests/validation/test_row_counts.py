from __future__ import annotations

from datetime import datetime, timezone, date

from sqlalchemy import create_engine

from follow_the_money.db import schema


def test_audit_row_counts_match_tables():
    engine = create_engine("sqlite:///:memory:")
    schema.metadata.create_all(engine)
    now = datetime.now(timezone.utc)

    with engine.begin() as conn:
        # Seed candidates and committees
        conn.execute(
            schema.candidates.insert(),
            [
                {"fec_id": "C1", "first_name": "Ann", "last_name": "Example", "created_at": now, "updated_at": now},
            ],
        )
        conn.execute(
            schema.committees.insert(),
            [
                {"fec_id": "CM1", "name": "PAC A", "created_at": now, "updated_at": now},
            ],
        )
        # Seed contributions
        conn.execute(
            schema.contributions.insert(),
            [
                {
                    "fec_record_id": "TX1",
                    "candidate_id": 1,
                    "committee_id": 1,
                    "amount": 100,
                    "transaction_dt": date.today(),
                    "cycle": "2024",
                    "is_individual": True,
                    "created_at": now,
                    "updated_at": now,
                }
            ],
        )
        # Create an audit run
        conn.execute(
            schema.ingest_run_audits.insert().values(
                run_key="test-run",
                source="test",
                status="running",
                started_at=now,
                rows_processed=1,
                checksum="abc",
                warnings=[],
                created_at=now,
                updated_at=now,
            )
        )

        candidate_rows = conn.execute(schema.candidates.select()).fetchall()
        committee_rows = conn.execute(schema.committees.select()).fetchall()
        contribution_rows = conn.execute(schema.contributions.select()).fetchall()

    assert len(candidate_rows) == 1
    assert len(committee_rows) == 1
    assert len(contribution_rows) == 1
