from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import create_engine, insert, select

from follow_the_money.db import schema
from follow_the_money.metrics import LeaningScoreCalculator


def seed_core_data(conn):
    now = datetime.now(timezone.utc)
    candidate_id = conn.execute(
        insert(schema.candidates).values(
            fec_id="C123",
            first_name="Ann",
            last_name="Example",
            party="DEM",
            created_at=now,
            updated_at=now,
        )
    ).inserted_primary_key[0]

    committee_left_id = conn.execute(
        insert(schema.committees).values(
            fec_id="L001",
            name="Left PAC",
            party="DEM",
            created_at=now,
            updated_at=now,
        )
    ).inserted_primary_key[0]

    committee_right_id = conn.execute(
        insert(schema.committees).values(
            fec_id="R001",
            name="Right PAC",
            party="REP",
            created_at=now,
            updated_at=now,
        )
    ).inserted_primary_key[0]

    employer_id = conn.execute(
        insert(schema.employers).values(
            name="ACME",
            normalized_name="ACME",
            employer_hash="abc",
            created_at=now,
            updated_at=now,
        )
    ).inserted_primary_key[0]

    conn.execute(
        insert(schema.contributions),
        [
            {
                "fec_record_id": "TX1",
                "candidate_id": candidate_id,
                "committee_id": committee_left_id,
                "employer_id": employer_id,
                "amount": 100,
                "transaction_dt": date.today(),
                "cycle": "2024",
                "is_individual": True,
                "created_at": now,
                "updated_at": now,
            },
            {
                "fec_record_id": "TX2",
                "candidate_id": candidate_id,
                "committee_id": committee_right_id,
                "employer_id": employer_id,
                "amount": 300,
                "transaction_dt": date.today(),
                "cycle": "2024",
                "is_individual": True,
                "created_at": now,
                "updated_at": now,
            },
        ],
    )


def test_leaning_scores_calculation():
    engine = create_engine("sqlite:///:memory:")
    schema.metadata.create_all(engine)

    with engine.begin() as conn:
        seed_core_data(conn)

    calculator = LeaningScoreCalculator(engine, lookback_days=365)
    calculator.run(as_of=date.today())

    with engine.begin() as conn:
        rows = conn.execute(select(schema.leaning_scores)).fetchall()

    assert len(rows) > 0
    candidate_scores = [row for row in rows if row.entity_type == "candidate"]
    assert candidate_scores
    score = candidate_scores[0]
    assert float(score.score) == 0.75
