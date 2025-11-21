from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Iterable, Mapping

from sqlalchemy import insert, select, update
from sqlalchemy.engine import Engine

from follow_the_money.db import schema
from follow_the_money.normalize.mappers import EmployerNormalizer


class NormalizationPipeline:
    """Transform staging tables into normalized entities."""

    def __init__(self, engine: Engine, *, employer_normalizer: EmployerNormalizer | None = None) -> None:
        self.engine = engine
        self.normalizer = employer_normalizer or EmployerNormalizer()

    def run(self, ingest_run_id: int) -> None:
        with self.engine.begin() as conn:
            candidate_rows = list(self._fetch_payloads(conn, schema.stg_fec_candidates, ingest_run_id))
            committee_rows = list(self._fetch_payloads(conn, schema.stg_fec_committees, ingest_run_id))
            receipt_rows = list(self._fetch_payloads(conn, schema.stg_fec_receipts, ingest_run_id))

            self._sync_candidates(conn, candidate_rows)
            self._sync_committees(conn, committee_rows)
            self._sync_committee_links(conn, receipt_rows)
            self._sync_contributions(conn, receipt_rows)

    def _fetch_payloads(self, conn, table, ingest_run_id: int) -> Iterable[Mapping[str, object]]:
        stmt = select(table.c.payload).where(table.c.ingest_run_id == ingest_run_id)
        for row in conn.execute(stmt):
            yield row.payload or {}

    def _sync_candidates(self, conn, rows: Iterable[Mapping[str, object]]) -> None:
        now = datetime.now(timezone.utc)
        for payload in rows:
            fec_id = payload.get("fec_id") or payload.get("candidate_id")
            if not fec_id:
                continue
            values = {
                "fec_id": fec_id,
                "first_name": payload.get("first_name"),
                "last_name": payload.get("last_name"),
                "party": payload.get("party"),
                "state": payload.get("state"),
                "district": payload.get("district"),
                "office": payload.get("office"),
                "status": payload.get("status"),
                "raw_metadata": payload,
                "updated_at": now,
            }
            values["created_at"] = payload.get("created_at") or now
            existing = conn.execute(
                select(schema.candidates.c.id).where(schema.candidates.c.fec_id == fec_id)
            ).scalar_one_or_none()
            if existing:
                conn.execute(
                    update(schema.candidates)
                    .where(schema.candidates.c.id == existing)
                    .values(values)
                )
            else:
                values["created_at"] = now
                conn.execute(insert(schema.candidates).values(values))

    def _sync_committees(self, conn, rows: Iterable[Mapping[str, object]]) -> None:
        now = datetime.now(timezone.utc)
        for payload in rows:
            fec_id = payload.get("fec_id") or payload.get("committee_id")
            if not fec_id:
                continue
            values = {
                "fec_id": fec_id,
                "name": payload.get("name") or payload.get("committee_name"),
                "committee_type": payload.get("type"),
                "designation": payload.get("designation"),
                "party": payload.get("party"),
                "connected_org": payload.get("connected_org"),
                "status": payload.get("status"),
                "raw_metadata": payload,
                "updated_at": now,
            }
            values["created_at"] = payload.get("created_at") or now
            existing = conn.execute(
                select(schema.committees.c.id).where(schema.committees.c.fec_id == fec_id)
            ).scalar_one_or_none()
            if existing:
                conn.execute(
                    update(schema.committees)
                    .where(schema.committees.c.id == existing)
                    .values(values)
                )
            else:
                values["created_at"] = now
                conn.execute(insert(schema.committees).values(values))

    def _sync_committee_links(self, conn, receipts: Iterable[Mapping[str, object]]) -> None:
        now = datetime.now(timezone.utc)
        for payload in receipts:
            candidate_fec = payload.get("cand_id")
            committee_fec = payload.get("committee_id") or payload.get("cmte_id")
            if not candidate_fec or not committee_fec:
                continue
            candidate_id = conn.execute(
                select(schema.candidates.c.id).where(schema.candidates.c.fec_id == candidate_fec)
            ).scalar_one_or_none()
            committee_id = conn.execute(
                select(schema.committees.c.id).where(schema.committees.c.fec_id == committee_fec)
            ).scalar_one_or_none()
            if not candidate_id or not committee_id:
                continue
            exists = conn.execute(
                select(schema.committee_candidate_links.c.committee_id).where(
                    schema.committee_candidate_links.c.committee_id == committee_id,
                    schema.committee_candidate_links.c.candidate_id == candidate_id,
                )
            ).scalar_one_or_none()
            if exists:
                continue
            conn.execute(
                insert(schema.committee_candidate_links).values(
                    committee_id=committee_id,
                    candidate_id=candidate_id,
                    relationship=payload.get("receipt_type"),
                    created_at=now,
                )
            )

    def _sync_contributions(self, conn, receipts: Iterable[Mapping[str, object]]) -> None:
        now = datetime.now(timezone.utc)
        for payload in receipts:
            tx_id = payload.get("fec_record_id") or payload.get("transaction_id")
            if not tx_id:
                continue
            existing = conn.execute(
                select(schema.contributions.c.id).where(schema.contributions.c.fec_record_id == tx_id)
            ).scalar_one_or_none()
            if existing:
                continue
            candidate_id = self._lookup_candidate(conn, payload.get("cand_id"))
            committee_id = self._lookup_committee(conn, payload.get("committee_id") or payload.get("cmte_id"))
            employer_id, industry_id = self._ensure_employer(conn, payload)
            amount = payload.get("amount")
            try:
                amount_decimal = Decimal(str(amount))
            except Exception:
                amount_decimal = Decimal("0")
            transaction_date = self._parse_date(payload.get("transaction_dt"))
            cycle = payload.get("cycle") or (transaction_date.year if transaction_date else None)
            conn.execute(
                insert(schema.contributions).values(
                    fec_record_id=tx_id,
                    candidate_id=candidate_id,
                    committee_id=committee_id,
                    employer_id=employer_id,
                    industry_id=industry_id,
                    donor_name=payload.get("donor_name"),
                    occupation=payload.get("occupation"),
                    amount=amount_decimal,
                    transaction_dt=transaction_date,
                    cycle=str(cycle) if cycle else None,
                    receipt_type=payload.get("receipt_type"),
                    memo_text=payload.get("memo_text"),
                    is_individual=bool(payload.get("is_individual", True)),
                    created_at=now,
                    updated_at=now,
                )
            )

    def _lookup_candidate(self, conn, fec_id: str | None) -> int | None:
        if not fec_id:
            return None
        return conn.execute(
            select(schema.candidates.c.id).where(schema.candidates.c.fec_id == fec_id)
        ).scalar_one_or_none()

    def _lookup_committee(self, conn, fec_id: str | None) -> int | None:
        if not fec_id:
            return None
        return conn.execute(
            select(schema.committees.c.id).where(schema.committees.c.fec_id == fec_id)
        ).scalar_one_or_none()

    def _ensure_employer(self, conn, payload: Mapping[str, object]) -> tuple[int | None, int | None]:
        employer_name = payload.get("employer") or "UNKNOWN"
        normalized = self.normalizer.normalize_name(str(employer_name))
        employer_hash = self.normalizer.employer_hash(normalized)
        now = datetime.now(timezone.utc)
        employer_id = conn.execute(
            select(schema.employers.c.id).where(schema.employers.c.employer_hash == employer_hash)
        ).scalar_one_or_none()
        if not employer_id:
            result = conn.execute(
                insert(schema.employers).values(
                    name=str(employer_name),
                    normalized_name=normalized,
                    employer_hash=employer_hash,
                    city=payload.get("city"),
                    state=payload.get("state"),
                    country=payload.get("country"),
                    created_at=now,
                    updated_at=now,
                )
            )
            employer_id = result.inserted_primary_key[0]
        industry_tuple = self.normalizer.classify(
            employer=normalized,
            occupation=str(payload.get("occupation", "")),
        )
        industry_id = None
        if industry_tuple:
            code, name, sector = industry_tuple
            industry_id = conn.execute(
                select(schema.industries.c.id).where(schema.industries.c.code == code)
            ).scalar_one_or_none()
            if not industry_id:
                result = conn.execute(
                    insert(schema.industries).values(
                        code=code,
                        name=name,
                        sector=sector,
                        created_at=now,
                        updated_at=now,
                    )
                )
                industry_id = result.inserted_primary_key[0]
            link_exists = conn.execute(
                select(schema.employer_industries.c.employer_id).where(
                    schema.employer_industries.c.employer_id == employer_id,
                    schema.employer_industries.c.industry_id == industry_id,
                )
            ).scalar_one_or_none()
            if not link_exists:
                conn.execute(
                    insert(schema.employer_industries).values(
                        employer_id=employer_id,
                        industry_id=industry_id,
                        confidence=1.0,
                        created_at=now,
                    )
                )
        return employer_id, industry_id

    def _parse_date(self, value: object) -> date | None:
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            try:
                return date.fromisoformat(value)
            except ValueError:
                return None
        return None
