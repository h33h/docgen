from docx import Document
from docx.shared import Pt

from docgen.config.document import DocumentFormatting
from docgen.document.formatter import DocumentFormatter


def test_formatter_applies_neutral_defaults():
    doc = Document()
    DocumentFormatter(DocumentFormatting()).apply(doc)
    section = doc.sections[0]
    assert round(section.left_margin.cm, 2) == 2
    assert round(section.right_margin.cm, 2) == 2
    assert doc.styles["Normal"].font.name == "Arial"
    assert doc.styles["Normal"].font.size == Pt(11)
    assert doc.styles["Heading 1"].font.size == Pt(18)


def test_formatter_applies_landscape_and_custom_spacing():
    config = DocumentFormatting.model_validate(
        {
            "orientation": "landscape",
            "margins": {"left_cm": 3, "right_cm": 1, "top_cm": 1.5, "bottom_cm": 1.5},
            "line_spacing": 1.5,
            "first_line_indent_cm": 1.25,
        }
    )
    doc = Document()
    DocumentFormatter(config).apply(doc)
    assert doc.sections[0].page_width > doc.sections[0].page_height
    assert round(doc.styles["Normal"].paragraph_format.first_line_indent.cm, 2) == 1.25
    assert doc.styles["Normal"].paragraph_format.line_spacing == 1.5


def test_formatter_enables_footer_page_number():
    config = DocumentFormatting.model_validate(
        {"page_number": {"position": "footer", "alignment": "right"}}
    )
    doc = Document()
    DocumentFormatter(config).apply(doc)
    assert "PAGE" in doc.sections[0].footer._element.xml


def test_formatter_leaves_page_number_off_by_default():
    doc = Document()
    DocumentFormatter(DocumentFormatting()).apply(doc)
    assert "PAGE" not in doc.sections[0].header._element.xml
    assert "PAGE" not in doc.sections[0].footer._element.xml
