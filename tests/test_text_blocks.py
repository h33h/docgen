from pathlib import Path

from docx import Document
from pydantic import TypeAdapter

from docgen.config.document import ContentBlock, DocumentConfig
from docgen.document.blocks import BlockRendererRegistry, RenderContext
from docgen.document.citations import CitationRegistry


def context():
    config = DocumentConfig.model_validate(
        {
            "kind": "document",
            "references": [{"id": "src", "text": "Source"}],
            "sections": [
                {"type": "content", "content": [{"type": "paragraph", "text": "x"}]}
            ],
        }
    )
    return RenderContext(
        Document(), config, CitationRegistry(config.references), Path.cwd(), None
    )


def test_text_blocks_render_in_order():
    ctx = context()
    raw_blocks = [
        {"type": "heading", "text": "Heading", "level": 2},
        {"type": "paragraph", "text": "Claim {{cite:src}}", "bold": True},
        {"type": "bullet_list", "items": ["One", "Two"]},
        {"type": "numbered_list", "items": ["First"], "start": 3},
        {"type": "page_break"},
    ]
    blocks = TypeAdapter(list[ContentBlock]).validate_python(raw_blocks)
    for block in blocks:
        BlockRendererRegistry.render(block, ctx)
    assert [paragraph.text for paragraph in ctx.doc.paragraphs[:5]] == [
        "Heading",
        "Claim [1]",
        "One",
        "Two",
        "First",
    ]
    assert ctx.doc.paragraphs[0].style.name == "Heading 2"
    assert ctx.doc.paragraphs[1].runs[0].bold is True
    assert ctx.doc.paragraphs[2].style.name == "List Bullet"
    assert "w:type=\"page\"" in ctx.doc.paragraphs[-1]._element.xml


def test_numbered_list_uses_requested_start():
    ctx = context()
    block = TypeAdapter(ContentBlock).validate_python(
        {"type": "numbered_list", "items": ["Three", "Four"], "start": 3}
    )
    BlockRendererRegistry.render(block, ctx)
    numbering_xml = ctx.doc.part.numbering_part.element.xml
    assert 'w:startOverride w:val="3"' in numbering_xml
    first_num_id = ctx.doc.paragraphs[0]._p.pPr.numPr.numId.val
    second_num_id = ctx.doc.paragraphs[1]._p.pPr.numPr.numId.val
    assert first_num_id == second_num_id


def test_non_toc_heading_is_visual_but_not_heading_style():
    ctx = context()
    block = TypeAdapter(ContentBlock).validate_python(
        {"type": "heading", "text": "Cover", "level": 1, "include_in_toc": False}
    )
    BlockRendererRegistry.render(block, ctx)
    assert ctx.doc.paragraphs[0].style.name == "Normal"
    assert ctx.doc.paragraphs[0].runs[0].bold is True
