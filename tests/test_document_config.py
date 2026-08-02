from pathlib import Path

import pytest
from pydantic import ValidationError

from docgen.config.document import DocumentConfig


def minimal_document(**overrides):
    data = {
        "kind": "document",
        "sections": [
            {
                "type": "content",
                "content": [{"type": "paragraph", "text": "Hello"}],
            }
        ],
    }
    data.update(overrides)
    return data


def test_document_defaults_are_neutral():
    config = DocumentConfig.model_validate(minimal_document())
    assert config.output == Path("document.docx")
    assert config.formatting.font.name == "Arial"
    assert config.formatting.font.size_pt == 11
    assert config.formatting.margins.left_cm == 2
    assert config.formatting.line_spacing == 1.15
    assert config.formatting.page_number.position == "off"


@pytest.mark.parametrize(
    "section",
    [
        {"type": "content"},
        {
            "type": "content",
            "content": [{"type": "paragraph", "text": "inline"}],
            "content_file": "content/body.json",
        },
    ],
)
def test_content_requires_exactly_one_source(section):
    with pytest.raises(ValidationError, match="exactly one"):
        DocumentConfig.model_validate({"kind": "document", "sections": [section]})


def test_unknown_fields_are_rejected():
    with pytest.raises(ValidationError, match="extra_forbidden"):
        DocumentConfig.model_validate(minimal_document(unknown=True))


def test_all_block_types_are_discriminated():
    blocks = [
        {"type": "paragraph", "text": "Text"},
        {"type": "heading", "text": "Heading", "level": 2},
        {"type": "bullet_list", "items": ["One"]},
        {"type": "numbered_list", "items": ["First"]},
        {"type": "table", "ref": "table-1"},
        {"type": "figure", "ref": "figure-1"},
        {"type": "page_break"},
    ]
    config = DocumentConfig.model_validate(
        minimal_document(
            resources={
                "tables": [{"id": "table-1", "rows": [["value"]]}],
                "figures": [
                    {"id": "figure-1", "type": "bar", "labels": ["A"], "values": [1]}
                ],
            },
            sections=[{"type": "content", "content": blocks}],
        )
    )
    assert [block.type for block in config.sections[0].content] == [
        "paragraph",
        "heading",
        "bullet_list",
        "numbered_list",
        "table",
        "figure",
        "page_break",
    ]


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"output": "wrong.pptx"}, "docx"),
        (
            {
                "resources": {
                    "tables": [
                        {"id": "same", "rows": [["a"]]},
                        {"id": "same", "rows": [["b"]]},
                    ]
                }
            },
            "duplicate table",
        ),
        (
            {"resources": {"tables": [{"id": "bad", "rows": [["a"], ["a", "b"]]}]}},
            "same width",
        ),
        (
            {
                "sections": [
                    {"type": "content", "content": [{"type": "table", "ref": "missing"}]}
                ]
            },
            "unknown table",
        ),
    ],
)
def test_invalid_document_graph_is_rejected(change, message):
    with pytest.raises(ValidationError, match=message):
        DocumentConfig.model_validate(minimal_document(**change))


def test_structure_connections_reference_known_nodes():
    with pytest.raises(ValidationError, match="unknown structure node"):
        DocumentConfig.model_validate(
            minimal_document(
                resources={
                    "figures": [
                        {
                            "id": "graph",
                            "type": "structure",
                            "nodes": [{"id": "root", "label": "Root"}],
                            "connections": [{"from": "root", "to": "missing"}],
                        }
                    ]
                }
            )
        )
