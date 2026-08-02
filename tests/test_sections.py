from pathlib import Path

from docx import Document

from docgen.config.document import DocumentConfig
from docgen.document.blocks import RenderContext
from docgen.document.citations import CitationRegistry
from docgen.document.sections import SectionRendererRegistry


def test_sections_render_content_toc_and_used_bibliography():
    config = DocumentConfig.model_validate(
        {
            "kind": "document",
            "references": [
                {"id": "used", "text": "Used source"},
                {"id": "unused", "text": "Unused source"},
            ],
            "sections": [
                {
                    "type": "content",
                    "title": "Results",
                    "content": [
                        {"type": "paragraph", "text": "Claim {{cite:used}}"}
                    ],
                },
                {"type": "toc", "title": "Contents", "min_level": 1, "max_level": 3},
                {"type": "bibliography", "title": "Sources"},
            ],
        }
    )
    doc = Document()
    context = RenderContext(doc, config, CitationRegistry(config.references), Path.cwd(), None)
    for section in config.sections:
        SectionRendererRegistry.render(section, context)

    texts = [paragraph.text for paragraph in doc.paragraphs]
    assert texts[0:2] == ["Results", "Claim [1]"]
    assert "Contents" in texts
    assert texts[-2:] == ["Sources", "1 Used source"]
    assert "Unused source" not in texts
    assert 'TOC \\o "1-3" \\h \\z \\u' in doc._element.xml
    assert "updateFields" in doc.settings._element.xml


def test_section_page_break_and_non_toc_title():
    config = DocumentConfig.model_validate(
        {
            "kind": "document",
            "sections": [
                {
                    "type": "content",
                    "title": "Cover",
                    "include_in_toc": False,
                    "page_break_before": True,
                    "content": [{"type": "paragraph", "text": "Body"}],
                }
            ],
        }
    )
    doc = Document()
    context = RenderContext(doc, config, CitationRegistry([]), Path.cwd(), None)
    SectionRendererRegistry.render(config.sections[0], context)
    assert "w:type=\"page\"" in doc.paragraphs[0]._element.xml
    assert doc.paragraphs[1].text == "Cover"
    assert doc.paragraphs[1].style.name == "Normal"
