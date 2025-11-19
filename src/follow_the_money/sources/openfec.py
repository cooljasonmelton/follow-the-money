from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Iterator, Mapping

from .http import HTTPClient
from .types import SourceMetadata


OPENFEC_BASE = "https://api.open.fec.gov/v1"


@dataclass(slots=True)
class OpenFECClient:
    api_key: str
    http: HTTPClient
    base_url: str = OPENFEC_BASE

    def _request_params(self, params: Mapping[str, Any] | None) -> Dict[str, Any]:
        merged: Dict[str, Any] = {"api_key": self.api_key}
        if params:
            merged.update(params)
        return merged

    def fetch(self, endpoint: str, params: Mapping[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.http.get(url, params=self._request_params(params))
        return response.json()

    def paginated_results(
        self,
        endpoint: str,
        params: Mapping[str, Any] | None = None,
    ) -> Iterator[dict[str, Any]]:
        page = 1
        combined_params = dict(params or {})
        while True:
            combined_params["page"] = page
            payload = self.fetch(endpoint, combined_params)
            results: Iterable[dict[str, Any]] = payload.get("results", [])
            for item in results:
                yield item
            pagination = payload.get("pagination") or {}
            if not pagination:
                break
            if page >= pagination.get("pages", page):
                break
            page += 1
