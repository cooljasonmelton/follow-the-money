"""Initial schema covering staging, normalized, and audit tables."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20251118_01"
down_revision = None
branch_labels = None
depends_on = None


def _timestamptz() -> sa.DateTime:
    return sa.DateTime(timezone=True)


def _create_staging(table_name: str) -> None:
    op.create_table(
        table_name,
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("ingest_run_id", sa.BigInteger(), sa.ForeignKey("ingest_run_audits.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_file", sa.String(length=255), nullable=False),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("cycle", sa.String(length=16), nullable=True),
        sa.Column("filing_date", sa.Date(), nullable=True),
        sa.Column("received_at", _timestamptz(), nullable=False),
        sa.Column("created_at", _timestamptz(), nullable=False),
        sa.Column("updated_at", _timestamptz(), nullable=False),
        sa.UniqueConstraint("source_file", "payload_hash", name=f"uq_{table_name}_source_file_payload_hash"),
    )


def upgrade() -> None:
    op.create_table(
        "ingest_run_audits",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("run_key", sa.String(length=64), nullable=False, unique=True),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("started_at", _timestamptz(), nullable=False),
        sa.Column("completed_at", _timestamptz()),
        sa.Column("rows_processed", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("checksum", sa.String(length=64)),
        sa.Column("warnings", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("error_message", sa.Text()),
        sa.Column("created_at", _timestamptz(), nullable=False),
        sa.Column("updated_at", _timestamptz(), nullable=False),
    )

    for table in (
        "stg_fec_receipts",
        "stg_fec_committees",
        "stg_fec_candidates",
        "stg_fec_individual_contributions",
    ):
        _create_staging(table)

    op.create_table(
        "candidates",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("fec_id", sa.String(length=32), nullable=False, unique=True),
        sa.Column("first_name", sa.String(length=128)),
        sa.Column("last_name", sa.String(length=128)),
        sa.Column("party", sa.String(length=32)),
        sa.Column("state", sa.String(length=2)),
        sa.Column("district", sa.String(length=8)),
        sa.Column("office", sa.String(length=8)),
        sa.Column("status", sa.String(length=32)),
        sa.Column("raw_metadata", postgresql.JSONB(astext_type=sa.Text())),
        sa.Column("created_at", _timestamptz(), nullable=False),
        sa.Column("updated_at", _timestamptz(), nullable=False),
    )

    op.create_table(
        "committees",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("fec_id", sa.String(length=32), nullable=False, unique=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("committee_type", sa.String(length=4)),
        sa.Column("designation", sa.String(length=2)),
        sa.Column("party", sa.String(length=32)),
        sa.Column("connected_org", sa.Text()),
        sa.Column("status", sa.String(length=32)),
        sa.Column("raw_metadata", postgresql.JSONB(astext_type=sa.Text())),
        sa.Column("created_at", _timestamptz(), nullable=False),
        sa.Column("updated_at", _timestamptz(), nullable=False),
    )

    op.create_table(
        "industries",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("code", sa.String(length=16), nullable=False, unique=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("sector", sa.String(length=255)),
        sa.Column("created_at", _timestamptz(), nullable=False),
        sa.Column("updated_at", _timestamptz(), nullable=False),
    )

    op.create_table(
        "employers",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False, unique=True),
        sa.Column("normalized_name", sa.String(length=255), nullable=False),
        sa.Column("employer_hash", sa.String(length=64), nullable=False, unique=True),
        sa.Column("city", sa.String(length=128)),
        sa.Column("state", sa.String(length=2)),
        sa.Column("country", sa.String(length=2)),
        sa.Column("created_at", _timestamptz(), nullable=False),
        sa.Column("updated_at", _timestamptz(), nullable=False),
    )

    op.create_table(
        "committee_candidate_links",
        sa.Column("committee_id", sa.BigInteger(), sa.ForeignKey("committees.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("candidate_id", sa.BigInteger(), sa.ForeignKey("candidates.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("relationship", sa.String(length=64)),
        sa.Column("created_at", _timestamptz(), nullable=False),
    )

    op.create_table(
        "employer_industries",
        sa.Column("employer_id", sa.BigInteger(), sa.ForeignKey("employers.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("industry_id", sa.BigInteger(), sa.ForeignKey("industries.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("confidence", sa.Numeric(5, 4), nullable=False, server_default="1.0"),
        sa.Column("created_at", _timestamptz(), nullable=False),
    )

    op.create_table(
        "contributions",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("fec_record_id", sa.String(length=64), nullable=False, unique=True),
        sa.Column("candidate_id", sa.BigInteger(), sa.ForeignKey("candidates.id", ondelete="SET NULL")),
        sa.Column("committee_id", sa.BigInteger(), sa.ForeignKey("committees.id", ondelete="SET NULL")),
        sa.Column("employer_id", sa.BigInteger(), sa.ForeignKey("employers.id", ondelete="SET NULL")),
        sa.Column("industry_id", sa.BigInteger(), sa.ForeignKey("industries.id", ondelete="SET NULL")),
        sa.Column("donor_name", sa.String(length=255)),
        sa.Column("occupation", sa.String(length=255)),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("transaction_dt", sa.Date(), nullable=False),
        sa.Column("cycle", sa.String(length=16), nullable=False),
        sa.Column("receipt_type", sa.String(length=8)),
        sa.Column("memo_text", sa.Text()),
        sa.Column("is_individual", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", _timestamptz(), nullable=False),
        sa.Column("updated_at", _timestamptz(), nullable=False),
        sa.CheckConstraint("amount >= 0", name="amount_non_negative"),
        postgresql_partition_by="RANGE (transaction_dt)",
    )

    op.create_index("ix_contributions_candidate_cycle", "contributions", ["candidate_id", "cycle"])
    op.create_index("ix_contributions_committee_cycle", "contributions", ["committee_id", "cycle"])
    op.create_index("ix_contributions_employer_cycle", "contributions", ["employer_id", "cycle"])

    leaning_enum = sa.Enum(
        "candidate",
        "committee",
        "employer",
        "industry",
        name="leaning_entity_type",
    )
    leaning_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "leaning_scores",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("entity_type", leaning_enum, nullable=False),
        sa.Column("entity_id", sa.BigInteger(), nullable=False),
        sa.Column("score", sa.Numeric(4, 3), nullable=False),
        sa.Column("left_amount", sa.Numeric(16, 2), nullable=False),
        sa.Column("right_amount", sa.Numeric(16, 2), nullable=False),
        sa.Column("sample_size", sa.Integer(), nullable=False),
        sa.Column("window_start", sa.Date(), nullable=False),
        sa.Column("window_end", sa.Date(), nullable=False),
        sa.Column("computed_at", _timestamptz(), nullable=False),
        sa.Column("methodology_version", sa.String(length=16), nullable=False, server_default="v1"),
        sa.Column("created_at", _timestamptz(), nullable=False),
        sa.UniqueConstraint("entity_type", "entity_id", "window_start", "window_end"),
    )


def downgrade() -> None:
    op.drop_table("leaning_scores")
    sa.Enum(name="leaning_entity_type").drop(op.get_bind(), checkfirst=True)
    op.drop_index("ix_contributions_employer_cycle", table_name="contributions")
    op.drop_index("ix_contributions_committee_cycle", table_name="contributions")
    op.drop_index("ix_contributions_candidate_cycle", table_name="contributions")
    op.drop_table("contributions")
    op.drop_table("employer_industries")
    op.drop_table("committee_candidate_links")
    op.drop_table("employers")
    op.drop_table("industries")
    op.drop_table("committees")
    op.drop_table("candidates")
    for table in (
        "stg_fec_individual_contributions",
        "stg_fec_candidates",
        "stg_fec_committees",
        "stg_fec_receipts",
    ):
        op.drop_table(table)
    op.drop_table("ingest_run_audits")
