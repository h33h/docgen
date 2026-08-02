from pathlib import Path

from docx import Document
import matplotlib.pyplot as plt
from pydantic import TypeAdapter

from docgen.config.document import ContentBlock, DocumentConfig
from docgen.document.blocks import BlockRendererRegistry, RenderContext
from docgen.document.citations import CitationRegistry
from docgen.document.resources import ResourceError, ResourceRegistry


def make_context(tmp_path: Path):
    image = tmp_path / "image.png"
    figure, axes = plt.subplots(figsize=(1, 1))
    axes.plot([0, 1], [0, 1])
    figure.savefig(image)
    plt.close(figure)
    config = DocumentConfig.model_validate(
        {
            "kind": "document",
            "resources": {
                "tables": [
                    {
                        "id": "table-1",
                        "headers": ["Name", "Value"],
                        "rows": [["A", "1"]],
                        "caption": "Result table",
                    }
                ],
                "figures": [
                    {
                        "id": "figure-1",
                        "type": "image",
                        "path": str(image),
                        "caption": "Result figure",
                    }
                ],
            },
            "sections": [
                {
                    "type": "content",
                    "content": [
                        {"type": "table", "ref": "table-1"},
                        {"type": "figure", "ref": "figure-1"},
                    ],
                }
            ],
        }
    )
    return RenderContext(
        Document(), config, CitationRegistry([]), tmp_path, tmp_path / "temp"
    )


def test_resource_blocks_render_table_and_image(tmp_path: Path):
    ctx = make_context(tmp_path)
    blocks = TypeAdapter(list[ContentBlock]).validate_python(
        [{"type": "table", "ref": "table-1"}, {"type": "figure", "ref": "figure-1"}]
    )
    for block in blocks:
        BlockRendererRegistry.render(block, ctx)
    assert len(ctx.doc.tables) == 1
    assert ctx.doc.tables[0].cell(0, 0).text == "Name"
    assert ctx.doc.tables[0].cell(1, 1).text == "1"
    assert "Result table" in [paragraph.text for paragraph in ctx.doc.paragraphs]
    assert len(ctx.doc.inline_shapes) == 1
    assert "Result figure" in [paragraph.text for paragraph in ctx.doc.paragraphs]


def test_resource_registry_rejects_unknown_ids(tmp_path: Path):
    registry = ResourceRegistry(make_context(tmp_path).config.resources)
    try:
        registry.table("missing")
    except ResourceError as error:
        assert "unknown table resource" in str(error)
    else:
        raise AssertionError("missing table must fail")


def test_chart_figure_is_materialized_only_in_temp_directory(tmp_path: Path):
    config = DocumentConfig.model_validate(
        {
            "kind": "document",
            "resources": {
                "figures": [
                    {"id": "chart", "type": "bar", "labels": ["A"], "values": [1]}
                ]
            },
            "sections": [
                {"type": "content", "content": [{"type": "figure", "ref": "chart"}]}
            ],
        }
    )
    temp_dir = tmp_path / "temp"
    context = RenderContext(Document(), config, CitationRegistry([]), tmp_path, temp_dir)
    block = TypeAdapter(ContentBlock).validate_python({"type": "figure", "ref": "chart"})
    BlockRendererRegistry.render(block, context)
    assert len(context.doc.inline_shapes) == 1
    assert (temp_dir / "chart.png").stat().st_size > 0
    assert not (tmp_path / "chart.png").exists()
