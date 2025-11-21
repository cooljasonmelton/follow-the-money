from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from sqlalchemy import create_engine

from datetime import datetime, UTC

from follow_the_money.db import schema
from follow_the_money.ingest import StagingLoader, iter_zip_tsv
from follow_the_money.metrics import LeaningScoreCalculator
from follow_the_money.normalize import NormalizationPipeline
from follow_the_money.sources import FECBulkDownloader, HTTPClient, OpenFECClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Follow the Money ETL runner")
    parser.add_argument("--database-url", default="sqlite:///follow-the-money.db")
    subparsers = parser.add_subparsers(dest="command")

    ingest_parser = subparsers.add_parser("ingest-backfill", help="Run historical ingest")
    ingest_parser.add_argument("--cycles", nargs="+", required=True)

    daily_parser = subparsers.add_parser("ingest-daily", help="Run daily ingest")
    daily_parser.add_argument("--cycle", required=True)

    subparsers.add_parser("normalize", help="Run normalization pipeline")
    subparsers.add_parser("compute-leaning", help="Compute leaning scores")

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    engine = create_engine(args.database_url)
    schema.metadata.create_all(engine)

    try:
        if args.command in {"ingest-backfill", "ingest-daily"}:
            loader = StagingLoader(engine)
            http = HTTPClient(timeout=60.0)
            storage_dir = Path("data/raw")
            downloader = FECBulkDownloader(http=http, storage_dir=storage_dir)

            cycles = args.cycles if args.command == "ingest-backfill" else [args.cycle]
            for cycle in cycles:
                logging.info("Ingesting cycle %s", cycle)
                logging.info("Downloading individual contributions ZIP for cycle %s...", cycle)
                result = downloader.download_individual_contributions(int(cycle))
                size_mb = result.metadata.bytes_written / (1024 * 1024)
                logging.info(
                    "Download complete: %s (%.2f MB)",
                    result.path,
                    size_mb,
                )
                timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
                run_key = f"{cycle}-raw-{timestamp}"
                run_id = loader.start_run(run_key=run_key, source="fec-indiv", metadata=result.metadata)
                rows = list(iter_zip_tsv(result.path))
                loader.load_raw_records(
                    "stg_fec_individual_contributions",
                    records=rows,
                    ingest_run_id=run_id,
                    source_file=result.path.name,
                    default_cycle=cycle,
                )
                loader.complete_run(run_id, status="succeeded", rows_processed=len(rows))
                logging.info("Cycle %s ingest completed (%d rows).", cycle, len(rows))

        elif args.command == "normalize":
            NormalizationPipeline(engine).run(ingest_run_id=_latest_run(engine))
        elif args.command == "compute-leaning":
            LeaningScoreCalculator(engine).run()
        else:
            logging.error("No command specified")
            return 1
    except RuntimeError as exc:
        logging.error(str(exc))
        return 1
    except KeyboardInterrupt:
        logging.warning("Ingest interrupted by user.")
        return 1

    return 0


def _latest_run(engine) -> int:
    with engine.begin() as conn:
        run = conn.execute(
            schema.ingest_run_audits.select().order_by(schema.ingest_run_audits.c.id.desc()).limit(1)
        ).fetchone()
        if not run:
            raise RuntimeError("No ingest run found")
        return run.id


if __name__ == "__main__":
    raise SystemExit(main())
