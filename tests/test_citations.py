import pytest

from docgen.config.document import ReferenceConfig
from docgen.document.citations import CitationError, CitationRegistry


def registry():
    return CitationRegistry(
        [
            ReferenceConfig(id="alpha", text="Alpha source"),
            ReferenceConfig(id="beta", text="Beta source"),
            ReferenceConfig(id="unused", text="Unused source"),
        ]
    )


def test_numbers_follow_first_mention_and_repeat():
    citations = registry()
    assert citations.replace("B {{cite:beta}} A {{cite:alpha}}") == "B [1] A [2]"
    assert citations.replace("Again {{cite:beta}}") == "Again [1]"
    assert [(number, ref.id) for number, ref in citations.used_entries()] == [
        (1, "beta"),
        (2, "alpha"),
    ]


def test_adjacent_citations_remain_separate():
    citations = registry()
    assert citations.replace("{{cite:alpha}}{{cite:beta}}") == "[1][2]"


def test_unknown_citation_fails():
    with pytest.raises(CitationError, match="missing"):
        registry().replace("{{cite:missing}}")
