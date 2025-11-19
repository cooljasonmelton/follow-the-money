"""Source connectors for campaign finance data."""

from .fec_bulk import FECBulkDownloader
from .openfec import OpenFECClient
from .types import DownloadResult, SourceMetadata
from .http import HTTPClient

__all__ = [
    "FECBulkDownloader",
    "OpenFECClient",
    "DownloadResult",
    "SourceMetadata",
    "HTTPClient",
]
