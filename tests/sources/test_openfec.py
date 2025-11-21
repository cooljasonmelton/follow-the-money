from __future__ import annotations

from follow_the_money.sources.http import HTTPClient
from follow_the_money.sources.openfec import OpenFECClient
from tests.sources.test_http import FakeResponse, fake_opener_factory


def test_paginated_results_iterates_all_pages() -> None:
    payload_page1 = b'{"results": [{"id": 1}], "pagination": {"page": 1, "pages": 2}}'
    payload_page2 = b'{"results": [{"id": 2}], "pagination": {"page": 2, "pages": 2}}'
    responses = [FakeResponse(payload_page1), FakeResponse(payload_page2)]
    client = HTTPClient(opener=fake_opener_factory(responses))
    openfec = OpenFECClient(api_key="demo", http=client)
    results = list(openfec.paginated_results("/candidates", params={"per_page": 1}))
    assert [item["id"] for item in results] == [1, 2]
