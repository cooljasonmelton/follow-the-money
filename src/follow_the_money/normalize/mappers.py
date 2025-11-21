from __future__ import annotations

import re
from dataclasses import dataclass
from hashlib import sha256
from typing import Iterable, Mapping, Tuple


def _strip_non_alnum(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", " ", text).strip()


@dataclass(slots=True)
class EmployerNormalizer:
    """Normalize employer names and infer industry codes from keyword heuristics."""

    keyword_map: Mapping[str, Tuple[str, str, str | None]] = None

    def __post_init__(self) -> None:
        if self.keyword_map is None:
            self.keyword_map = {
                "tech": ("TECH", "Technology", "Technology"),
                "software": ("TECH", "Technology", "Technology"),
                "bank": ("FIN", "Financial Services", "Finance"),
                "finance": ("FIN", "Financial Services", "Finance"),
                "construction": ("CONS", "Construction", "Industrials"),
                "education": ("EDU", "Education", "Public Sector"),
            }

    def normalize_name(self, name: str | None) -> str:
        if not name:
            return "UNKNOWN"
        normalized = _strip_non_alnum(name).upper()
        tokens = [token for token in normalized.split() if token not in {"INC", "INCORPORATED", "CORP", "CORPORATION", "LLC", "LTD", "COMPANY", "CO"}]
        return " ".join(tokens) if tokens else "UNKNOWN"

    def employer_hash(self, normalized_name: str) -> str:
        return sha256(normalized_name.encode("utf-8")).hexdigest()

    def classify(self, *, employer: str | None, occupation: str | None) -> Tuple[str, str, str | None] | None:
        text = f"{employer or ''} {occupation or ''}".lower()
        for keyword, (code, name, sector) in self.keyword_map.items():
            if keyword in text:
                return code, name, sector
        return None
