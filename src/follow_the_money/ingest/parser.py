from __future__ import annotations

import csv
import io
import zipfile
from pathlib import Path
from typing import Iterable, Iterator, Sequence


def iter_zip_tsv(
    zip_path: str | Path,
    *,
    fieldnames: Sequence[str] | None = None,
    encoding: str = "latin-1",
    delimiter: str = "\t",
) -> Iterator[dict[str, str]]:
    """Yield rows from the first file inside a FEC bulk ZIP as dictionaries."""

    path = Path(zip_path)
    if not path.exists():
        raise FileNotFoundError(path)

    with zipfile.ZipFile(path) as zf:
        if not zf.namelist():
            return
        inner_name = zf.namelist()[0]
        with zf.open(inner_name) as raw:
            text_stream = io.TextIOWrapper(raw, encoding=encoding, newline="")
            if fieldnames:
                reader = csv.DictReader(text_stream, fieldnames=fieldnames, delimiter=delimiter)
            else:
                reader = csv.DictReader(text_stream, delimiter=delimiter)
            for row in reader:
                yield {key: (value.strip() if isinstance(value, str) else value) for key, value in row.items() if key is not None}
