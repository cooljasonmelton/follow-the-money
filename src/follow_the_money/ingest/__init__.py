"""Ingestion utilities for staging raw data."""

from .parser import iter_zip_tsv
from .staging_loader import StagingLoader

__all__ = ["iter_zip_tsv", "StagingLoader"]
