from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence
from urllib.error import HTTPError
from datetime import datetime, timezone
from hashlib import sha256

from .http import HTTPClient
from .types import DownloadResult, SourceMetadata


FEC_BULK_BASE = "https://www.fec.gov/files/bulk-downloads"


@dataclass(slots=True)
class FECBulkDownloader:
    http: HTTPClient
    storage_dir: Path

    def _ensure_storage(self) -> None:
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def download_receipts_zip(self, cycle: int, *, kind: str = "receipts") -> DownloadResult:
        """Download zipped receipts (schedule A/B) for the given cycle."""
        suffix = str(cycle)[-2:]
        filenames = [f"{cycle}{kind}.zip", f"{kind}{suffix}.zip"]
        return self._download_from_candidates(filenames, cycle)

    def download_individual_contributions(self, cycle: int) -> DownloadResult:
        suffix = str(cycle)[-2:]
        filenames = [f"{cycle}indiv.zip", f"indiv{suffix}.zip"]
        return self._download_from_candidates(filenames, cycle)

    def download_committees(self, cycle: int) -> DownloadResult:
        suffix = str(cycle)[-2:]
        filenames = [f"{cycle}cm.zip", f"cm{suffix}.zip"]
        return self._download_from_candidates(filenames, cycle)

    def download_candidates(self, cycle: int) -> DownloadResult:
        suffix = str(cycle)[-2:]
        filenames = [f"weball{suffix}.zip", f"{cycle}cn.zip"]
        return self._download_from_candidates(filenames, cycle)

    def _download_from_candidates(self, filenames: Sequence[str], cycle: int) -> DownloadResult:
        last_error: RuntimeError | None = None
        for name in filenames:
            try:
                return self._download_file(name, cycle_folder=str(cycle))
            except RuntimeError as exc:
                last_error = exc
        if last_error:
            raise last_error
        raise RuntimeError("Unable to download requested FEC file.")

    def _download_file(self, filename: str, cycle_folder: str | None = None) -> DownloadResult:
        self._ensure_storage()
        urls = []
        if cycle_folder:
            urls.append(f"{FEC_BULK_BASE}/{cycle_folder}/{filename}")
        urls.append(f"{FEC_BULK_BASE}/{filename}")
        dest = self.storage_dir / filename
        if dest.exists() and dest.stat().st_size > 0:
            # Reuse existing file and emit synthetic metadata
            logger.info("Using existing download: %s", dest)
            checksum = sha256()
            bytes_written = 0
            with dest.open("rb") as fp:
                for chunk in iter(lambda: fp.read(1024 * 1024), b""):
                    checksum.update(chunk)
                    bytes_written += len(chunk)
            now = datetime.now(timezone.utc)
            metadata = SourceMetadata(
                url=str(urls[0]),
                status_code=200,
                headers={},
                params=None,
                bytes_written=bytes_written,
                checksum=checksum.hexdigest(),
                requested_at=now,
                completed_at=now,
            )
            return DownloadResult(path=dest, metadata=metadata)
        last_error: RuntimeError | None = None
        for url in urls:
            try:
                return self.http.stream_to_file(url, dest)
            except HTTPError as exc:
                if exc.code == 404:
                    last_error = RuntimeError(f"FEC bulk file not available at {url}")
                else:
                    last_error = RuntimeError(f"Failed to download {url}: {exc}")
                last_error.__cause__ = exc
        if last_error:
            raise last_error
        raise RuntimeError(f"Unable to download {filename}")
