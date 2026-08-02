from pathlib import Path

import pytest
from pydantic import ValidationError

from docgen.config.presentation import PresentationConfig


def minimal_presentation(**overrides):
    data = {
        "kind": "presentation",
        "title": "Demo",
        "slides": [
            {"type": "title"},
            {"type": "text", "title": "One", "text": "Body"},
        ],
    }
    data.update(overrides)
    return data


def test_minimal_presentation_is_valid():
    config = PresentationConfig.model_validate(minimal_presentation())
    assert config.output == Path("presentation.pptx")
    assert config.theme == "classic"
    assert [slide.type for slide in config.slides] == ["title", "text"]


def test_slide_types_require_their_own_fields():
    with pytest.raises(ValidationError):
        PresentationConfig.model_validate(
            minimal_presentation(slides=[{"type": "table", "items": []}])
        )


def test_presentation_rejects_unknown_fields():
    with pytest.raises(ValidationError, match="extra_forbidden"):
        PresentationConfig.model_validate(minimal_presentation(unexpected="value"))


def test_presentation_rejects_unknown_resource_ref():
    with pytest.raises(ValidationError, match="unknown table"):
        PresentationConfig.model_validate(
            minimal_presentation(slides=[{"type": "table", "ref": "missing"}])
        )


def test_presentation_requires_pptx_output():
    with pytest.raises(ValidationError, match="pptx"):
        PresentationConfig.model_validate(minimal_presentation(output="slides.docx"))


def test_all_slide_types_are_discriminated():
    slides = [
        {"type": "title", "lines": ["Line"]},
        {"type": "contents", "items": ["One"]},
        {"type": "text", "title": "Text", "text": "Body"},
        {"type": "bullets", "title": "List", "items": ["One"]},
        {"type": "two_column", "title": "Compare", "left": ["L"], "right": ["R"]},
        {"type": "table", "ref": "table-1"},
        {"type": "figure", "ref": "figure-1"},
        {"type": "sources", "items": ["Source"]},
        {"type": "thanks"},
    ]
    config = PresentationConfig.model_validate(
        minimal_presentation(
            resources={
                "tables": [{"id": "table-1", "rows": [["value"]]}],
                "figures": [
                    {"id": "figure-1", "type": "bar", "labels": ["A"], "values": [1]}
                ],
            },
            slides=slides,
        )
    )
    assert [slide.type for slide in config.slides] == [slide["type"] for slide in slides]
