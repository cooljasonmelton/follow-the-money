from __future__ import annotations

import io
from pathlib import Path
from typing import Any

from follow_the_money.sources.http import HTTPClient, SimpleResponse


class FakeResponse:
    def __init__(self, body: bytes, status: int = 200, headers: dict[str, str] | None = None) -> None:
        self._buffer = io.BytesIO(body)
        self._status = status
        self._headers = headers or {}

    def read(self, size: int = -1) -> bytes:
        return self._buffer.read(size)

    def getcode(self) -> int:
        return self._status

    def getheaders(self) -> list[tuple[str, str]]:
        return list(self._headers.items())

    def close(self) -> None:
        self._buffer.close()


def fake_opener_factory(responses: list[FakeResponse]):
    def opener(request: Any) -> FakeResponse:
        return responses.pop(0)

    return opener


def test_http_get_returns_response() -> None:
    responses = [FakeResponse(b'{"ok": true}', headers={"Content-Type": "application/json"})]
    client = HTTPClient(opener=fake_opener_factory(responses))
    resp = client.get("https://example.com/api")
    assert isinstance(resp, SimpleResponse)
    assert resp.status_code == 200
    assert resp.json()["ok"] is True


def test_stream_to_file_writes_bytes(tmp_path: Path) -> None:
    responses = [FakeResponse(b"abc123", headers={"Content-Length": "6"})]
    client = HTTPClient(opener=fake_opener_factory(responses))
    dest = tmp_path / "file.zip"
    result = client.stream_to_file("https://example.com/file.zip", dest)
    assert dest.read_bytes() == b"abc123"
    assert result.metadata.bytes_written == 6
    assert len(result.metadata.checksum) == 64
