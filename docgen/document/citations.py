"""Deterministic inline citation numbering."""

from __future__ import annotations

import re

from docgen.config.document import ReferenceConfig

_CITATION_PATTERN = re.compile(r"\{\{cite:([A-Za-z0-9_.-]+)\}\}")


class CitationError(ValueError):
    pass


class CitationRegistry:
    def __init__(self, references: list[ReferenceConfig]):
        self._references = {reference.id: reference for reference in references}
        self._numbers: dict[str, int] = {}
        self._used_ids: list[str] = []

    def replace(self, text: str) -> str:
        def replacement(match: re.Match[str]) -> str:
            reference_id = match.group(1)
            if reference_id not in self._references:
                raise CitationError(f"unknown citation: {reference_id}")
            if reference_id not in self._numbers:
                self._used_ids.append(reference_id)
                self._numbers[reference_id] = len(self._used_ids)
            return f"[{self._numbers[reference_id]}]"

        return _CITATION_PATTERN.sub(replacement, text)

    def used_entries(self) -> list[tuple[int, ReferenceConfig]]:
        return [
            (self._numbers[reference_id], self._references[reference_id])
            for reference_id in self._used_ids
        ]
