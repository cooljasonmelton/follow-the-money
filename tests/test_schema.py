from __future__ import annotations

from follow_the_money.db import schema


def test_staging_tables_have_consistent_columns() -> None:
    expected_columns = {
        "ingest_run_id",
        "source_file",
        "payload_hash",
        "payload",
        "cycle",
        "filing_date",
        "received_at",
        "created_at",
        "updated_at",
    }
    for table_name in (
        "stg_fec_receipts",
        "stg_fec_committees",
        "stg_fec_candidates",
        "stg_fec_individual_contributions",
    ):
        columns = set(schema.metadata.tables[table_name].columns.keys())
        assert expected_columns.issubset(columns), f"{table_name} missing expected staging columns"


def test_contributions_table_indexes() -> None:
    contributions = schema.metadata.tables["contributions"]
    index_names = {index.name for index in contributions.indexes}
    assert "ix_contributions_candidate_cycle" in index_names
    assert "ix_contributions_committee_cycle" in index_names
    assert "ix_contributions_employer_cycle" in index_names


def test_leaning_scores_uniqueness() -> None:
    leaning_scores = schema.metadata.tables["leaning_scores"]
    unique_constraints = {constraint.name for constraint in leaning_scores.constraints if getattr(constraint, "name", None)}
    assert "uq_leaning_scores_entity_type_entity_id_window_start_window_end" in unique_constraints
