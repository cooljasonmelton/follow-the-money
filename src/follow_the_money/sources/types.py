from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping, MutableMapping


@dataclass(slots=True, frozen=True)
class SourceMetadata:
    url: str
    status_code: int
    headers: Mapping[str, Any]
    params: Mapping[str, Any] | None
    bytes_written: int
    checksum: str
    requested_at: datetime
    completed_at: datetime


@dataclass(slots=True, frozen=True)
class DownloadResult:
    path: Path
    metadata: SourceMetadata


MutableHeaders = MutableMapping[str, str]
