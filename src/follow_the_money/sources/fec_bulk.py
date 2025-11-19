from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

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
        filename = f"{cycle}{kind}.zip"
        return self._download_file(filename)

    def download_individual_contributions(self, cycle: int) -> DownloadResult:
        filename = f"{cycle}indiv.zip"
        return self._download_file(filename)

    def download_committees(self, cycle: int) -> DownloadResult:
        filename = f"{cycle}cm.zip"
        return self._download_file(filename)

    def download_candidates(self, cycle: int) -> DownloadResult:
        filename = f"{cycle}cn.zip"
        return self._download_file(filename)

    def _download_file(self, filename: str) -> DownloadResult:
        self._ensure_storage()
        url = f"{FEC_BULK_BASE}/{filename}"
        dest = self.storage_dir / filename
        return self.http.stream_to_file(url, dest)
