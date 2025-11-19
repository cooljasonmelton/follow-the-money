"""Database schema metadata for Follow the Money."""

from __future__ import annotations

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    Numeric,
    String,
    Table,
    Text,
    UniqueConstraint,
)

# Use portable JSON type for metadata-level introspection. JSONB is applied via migrations.
JSONType = JSON

naming_convention = {
    "ix": "ix_%(column_0_N_label)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_N_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=naming_convention)


ingest_run_audits = Table(
    "ingest_run_audits",
    metadata,
    Column("id", BigInteger, primary_key=True),
    Column("run_key", String(64), nullable=False, unique=True),
    Column("source", String(64), nullable=False),
    Column("status", String(32), nullable=False),
    Column("started_at", DateTime(timezone=True), nullable=False),
    Column("completed_at", DateTime(timezone=True)),
    Column("rows_processed", BigInteger, nullable=False, default=0),
    Column("checksum", String(64)),
    Column("warnings", JSONType, nullable=False, default=list),
    Column("error_message", Text),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)


def staging_table(name: str) -> Table:
    """Create a staging table with consistent columns for raw payloads."""

    return Table(
        name,
        metadata,
        Column("id", BigInteger, primary_key=True),
        Column("ingest_run_id", ForeignKey("ingest_run_audits.id", ondelete="CASCADE"), nullable=False),
        Column("source_file", String(255), nullable=False),
        Column("payload_hash", String(64), nullable=False),
        Column("payload", JSONType, nullable=False),
        Column("cycle", String(16), nullable=True),
        Column("filing_date", Date),
        Column("received_at", DateTime(timezone=True), nullable=False),
        Column("created_at", DateTime(timezone=True), nullable=False),
        Column("updated_at", DateTime(timezone=True), nullable=False),
        UniqueConstraint("source_file", "payload_hash"),
    )


stg_fec_receipts = staging_table("stg_fec_receipts")
stg_fec_committees = staging_table("stg_fec_committees")
stg_fec_candidates = staging_table("stg_fec_candidates")
stg_fec_individual_contributions = staging_table("stg_fec_individual_contributions")


candidates = Table(
    "candidates",
    metadata,
    Column("id", BigInteger, primary_key=True),
    Column("fec_id", String(32), nullable=False, unique=True),
    Column("first_name", String(128)),
    Column("last_name", String(128)),
    Column("party", String(32)),
    Column("state", String(2)),
    Column("district", String(8)),
    Column("office", String(8)),
    Column("status", String(32)),
    Column("raw_metadata", JSONType),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

committees = Table(
    "committees",
    metadata,
    Column("id", BigInteger, primary_key=True),
    Column("fec_id", String(32), nullable=False, unique=True),
    Column("name", Text, nullable=False),
    Column("committee_type", String(4)),
    Column("designation", String(2)),
    Column("party", String(32)),
    Column("connected_org", Text),
    Column("status", String(32)),
    Column("raw_metadata", JSONType),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

committee_candidate_links = Table(
    "committee_candidate_links",
    metadata,
    Column("committee_id", ForeignKey("committees.id", ondelete="CASCADE"), primary_key=True),
    Column("candidate_id", ForeignKey("candidates.id", ondelete="CASCADE"), primary_key=True),
    Column("relationship", String(64)),
    Column("created_at", DateTime(timezone=True), nullable=False),
)

industries = Table(
    "industries",
    metadata,
    Column("id", BigInteger, primary_key=True),
    Column("code", String(16), unique=True, nullable=False),
    Column("name", String(255), nullable=False),
    Column("sector", String(255)),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

employers = Table(
    "employers",
    metadata,
    Column("id", BigInteger, primary_key=True),
    Column("name", String(255), nullable=False, unique=True),
    Column("normalized_name", String(255), nullable=False),
    Column("employer_hash", String(64), nullable=False, unique=True),
    Column("city", String(128)),
    Column("state", String(2)),
    Column("country", String(2)),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

employer_industries = Table(
    "employer_industries",
    metadata,
    Column("employer_id", ForeignKey("employers.id", ondelete="CASCADE"), primary_key=True),
    Column("industry_id", ForeignKey("industries.id", ondelete="CASCADE"), primary_key=True),
    Column("confidence", Numeric(5, 4), nullable=False, default=1.0),
    Column("created_at", DateTime(timezone=True), nullable=False),
)

contributions = Table(
    "contributions",
    metadata,
    Column("id", BigInteger, primary_key=True),
    Column("fec_record_id", String(64), nullable=False, unique=True),
    Column("candidate_id", ForeignKey("candidates.id", ondelete="SET NULL")),
    Column("committee_id", ForeignKey("committees.id", ondelete="SET NULL")),
    Column("employer_id", ForeignKey("employers.id", ondelete="SET NULL")),
    Column("industry_id", ForeignKey("industries.id", ondelete="SET NULL")),
    Column("donor_name", String(255)),
    Column("occupation", String(255)),
    Column("amount", Numeric(14, 2), nullable=False),
    Column("transaction_dt", Date, nullable=False),
    Column("cycle", String(16), nullable=False),
    Column("receipt_type", String(8)),
    Column("memo_text", Text),
    Column("is_individual", Boolean, nullable=False, default=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
    Index("ix_contributions_candidate_cycle", "candidate_id", "cycle"),
    Index("ix_contributions_committee_cycle", "committee_id", "cycle"),
    Index("ix_contributions_employer_cycle", "employer_id", "cycle"),
    CheckConstraint("amount >= 0", name="amount_non_negative"),
)

leaning_entity_enum = Enum(
    "candidate",
    "committee",
    "employer",
    "industry",
    name="leaning_entity_type",
)

leaning_scores = Table(
    "leaning_scores",
    metadata,
    Column("id", BigInteger, primary_key=True),
    Column("entity_type", leaning_entity_enum, nullable=False),
    Column("entity_id", BigInteger, nullable=False),
    Column("score", Numeric(4, 3), nullable=False),
    Column("left_amount", Numeric(16, 2), nullable=False),
    Column("right_amount", Numeric(16, 2), nullable=False),
    Column("sample_size", Integer, nullable=False),
    Column("window_start", Date, nullable=False),
    Column("window_end", Date, nullable=False),
    Column("computed_at", DateTime(timezone=True), nullable=False),
    Column("methodology_version", String(16), nullable=False, default="v1"),
    UniqueConstraint("entity_type", "entity_id", "window_start", "window_end"),
    Column("created_at", DateTime(timezone=True), nullable=False),
)
