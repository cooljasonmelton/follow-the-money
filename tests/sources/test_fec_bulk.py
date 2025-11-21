from __future__ import annotations

from follow_the_money.sources.fec_bulk import FECBulkDownloader
from follow_the_money.sources.http import HTTPClient
from tests.sources.test_http import FakeResponse, fake_opener_factory


def test_downloaders_write_files(tmp_path) -> None:
    responses = [FakeResponse(b"zip-bytes")]
    client = HTTPClient(opener=fake_opener_factory(responses))
    downloader = FECBulkDownloader(http=client, storage_dir=tmp_path)
    result = downloader.download_individual_contributions(2024)
    assert result.path.exists()
    assert result.metadata.bytes_written == len(b"zip-bytes")
    assert "2024indiv.zip" in result.metadata.url
