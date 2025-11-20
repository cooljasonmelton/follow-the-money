from __future__ import annotations

import hashlib
import json
import time
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping
from urllib.parse import urlencode, urljoin
from urllib.request import OpenerDirector, Request, build_opener
import logging

from .types import DownloadResult, SourceMetadata

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class SimpleResponse:
    status_code: int
    headers: dict[str, str]
    content: bytes

    def json(self) -> Any:
        return json.loads(self.content.decode("utf-8"))


class HTTPClient:
    def __init__(
        self,
        base_url: str | None = None,
        *,
        timeout: float = 30.0,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
        headers: Mapping[str, str] | None = None,
        opener: OpenerDirector | Callable[[Request], Any] | None = None,
        chunk_size: int = 1024 * 64,
    ) -> None:
        self._base_url = base_url.rstrip("/") if base_url else None
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self._headers = dict(headers or {})
        self._opener = opener or build_opener()
        self.chunk_size = chunk_size

    def _build_url(self, url: str, params: Mapping[str, Any] | None) -> str:
        resolved = urljoin(f"{self._base_url}/", url.lstrip("/")) if self._base_url else url
        if params:
            encoded = urlencode(params, doseq=True)
            separator = "&" if "?" in resolved else "?"
            return f"{resolved}{separator}{encoded}"
        return resolved

    def _open(self, request: Request):
        if isinstance(self._opener, OpenerDirector):
            return self._opener.open(request, timeout=self.timeout)
        return self._opener(request)

    def get(self, url: str, *, params: Mapping[str, Any] | None = None) -> SimpleResponse:
        request_url = self._build_url(url, params)
        req = Request(request_url, headers=self._headers)
        last_exc: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                with closing(self._open(req)) as resp:
                    content = resp.read()
                    headers = dict(resp.getheaders())
                    status = resp.getcode()
                    if status >= 400:
                        raise RuntimeError(f"HTTP {status}: {request_url}")
                    return SimpleResponse(status_code=status, headers=headers, content=content)
            except Exception as exc:  # pragma: no cover - validated via tests by ensuring no retries triggered
                last_exc = exc
                if attempt == self.max_retries:
                    raise
                time.sleep(self.backoff_factor * (2 ** (attempt - 1)))
        assert last_exc  # pragma: no cover
        raise last_exc

    def stream_to_file(
        self,
        url: str,
        dest_path: Path | str,
        *,
        params: Mapping[str, Any] | None = None,
    ) -> DownloadResult:
        request_url = self._build_url(url, params)
        req = Request(request_url, headers=self._headers)
        requested_at = datetime.now(timezone.utc)
        next_log_threshold = 100 * 1024 * 1024  # 100MB
        with closing(self._open(req)) as resp, Path(dest_path).open("wb") as fp:
            checksum = hashlib.sha256()
            bytes_written = 0
            while True:
                chunk = resp.read(self.chunk_size)
                if not chunk:
                    break
                checksum.update(chunk)
                fp.write(chunk)
                bytes_written += len(chunk)
                if bytes_written >= next_log_threshold:
                    logger.info(
                        "Downloaded %.2f MB from %s",
                        bytes_written / (1024 * 1024),
                        request_url,
                    )
                    next_log_threshold += 100 * 1024 * 1024
            status = resp.getcode()
            headers = dict(resp.getheaders())
        completed_at = datetime.now(timezone.utc)
        metadata = SourceMetadata(
            url=request_url,
            status_code=status,
            headers=headers,
            params=params,
            bytes_written=bytes_written,
            checksum=checksum.hexdigest(),
            requested_at=requested_at,
            completed_at=completed_at,
        )
        return DownloadResult(path=Path(dest_path), metadata=metadata)
