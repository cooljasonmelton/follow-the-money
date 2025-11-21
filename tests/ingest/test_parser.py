from __future__ import annotations

import csv
import zipfile
from pathlib import Path

from follow_the_money.ingest import iter_zip_tsv


def test_iter_zip_tsv_yields_rows(tmp_path: Path) -> None:
    path = tmp_path / "sample.zip"
    rows = [
        {"id": "1", "amount": "100"},
        {"id": "2", "amount": "200"},
    ]
    with zipfile.ZipFile(path, "w") as zf:
        with zf.open("sample.txt", "w") as fp:
            fp.write("id\tamount\n".encode("latin-1"))
            fp.write("1\t100\n".encode("latin-1"))
            fp.write("2\t200\n".encode("latin-1"))

    parsed = list(iter_zip_tsv(path))
    assert parsed == rows
