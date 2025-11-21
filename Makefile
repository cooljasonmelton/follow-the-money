.PHONY: ingest-backfill ingest-daily normalize compute-leaning fmt lint test

PYTHON ?= python3
DATABASE_URL ?= sqlite:///follow-the-money.db
CYCLE ?= 2024

ingest-backfill:
	$(PYTHON) -m follow_the_money.cli --database-url $(DATABASE_URL) ingest-backfill --cycles $(CYCLE)

ingest-daily:
	$(PYTHON) -m follow_the_money.cli --database-url $(DATABASE_URL) ingest-daily --cycle 2024

normalize:
	$(PYTHON) -m follow_the_money.cli --database-url $(DATABASE_URL) normalize

compute-leaning:
	$(PYTHON) -m follow_the_money.cli --database-url $(DATABASE_URL) compute-leaning

fmt:
	$(PYTHON) -m black src tests

lint:
	$(PYTHON) -m ruff check src tests

test:
	pytest
