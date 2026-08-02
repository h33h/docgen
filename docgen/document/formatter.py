"""Neutral DOCX page and style formatting."""

from __future__ import annotations

from docx.enum.section import WD_ORIENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt

from docgen.config.common import Alignment
from docgen.config.document import DocumentFormatting


_ALIGNMENTS = {
    Alignment.LEFT: WD_ALIGN_PARAGRAPH.LEFT,
    Alignment.CENTER: WD_ALIGN_PARAGRAPH.CENTER,
    Alignment.RIGHT: WD_ALIGN_PARAGRAPH.RIGHT,
    Alignment.JUSTIFY: WD_ALIGN_PARAGRAPH.JUSTIFY,
}


def apply_run_font(
    run,
    name: str,
    size: float,
    bold: bool = False,
    italic: bool = False,
) -> None:
    run.font.name = name
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), name)


class DocumentFormatter:
    def __init__(self, config: DocumentFormatting):
        self.config = config

    def apply(self, doc) -> None:
        self._apply_sections(doc)
        self._apply_normal_style(doc)
        self._apply_heading_styles(doc)
        self._apply_page_number(doc)

    def _apply_sections(self, doc) -> None:
        for section in doc.sections:
            if self.config.page_size == "A4":
                width, height = Cm(21), Cm(29.7)
            else:
                width, height = Inches(8.5), Inches(11)
            if self.config.orientation == "landscape":
                section.orientation = WD_ORIENT.LANDSCAPE
                width, height = height, width
            else:
                section.orientation = WD_ORIENT.PORTRAIT
            section.page_width = width
            section.page_height = height
            section.left_margin = Cm(self.config.margins.left_cm)
            section.right_margin = Cm(self.config.margins.right_cm)
            section.top_margin = Cm(self.config.margins.top_cm)
            section.bottom_margin = Cm(self.config.margins.bottom_cm)

    def _apply_normal_style(self, doc) -> None:
        style = doc.styles["Normal"]
        style.font.name = self.config.font.name
        style.font.size = Pt(self.config.font.size_pt)
        style._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), self.config.font.name)
        paragraph = style.paragraph_format
        paragraph.line_spacing = self.config.line_spacing
        paragraph.first_line_indent = Cm(self.config.first_line_indent_cm)
        paragraph.space_before = Pt(self.config.space_before_pt)
        paragraph.space_after = Pt(self.config.space_after_pt)

    def _apply_heading_styles(self, doc) -> None:
        for level, size in self.config.heading_sizes_pt.items():
            style = doc.styles[f"Heading {level}"]
            style.font.name = self.config.font.name
            style.font.size = Pt(size)
            style.font.bold = True
            style._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), self.config.font.name)

    def _apply_page_number(self, doc) -> None:
        page_number = self.config.page_number
        if page_number.position == "off":
            return
        for section in doc.sections:
            container = section.header if page_number.position == "header" else section.footer
            paragraph = container.paragraphs[0]
            paragraph.alignment = _ALIGNMENTS[page_number.alignment]
            run = paragraph.add_run()
            field_begin = OxmlElement("w:fldChar")
            field_begin.set(qn("w:fldCharType"), "begin")
            instruction = OxmlElement("w:instrText")
            instruction.set(qn("xml:space"), "preserve")
            instruction.text = " PAGE "
            field_end = OxmlElement("w:fldChar")
            field_end.set(qn("w:fldCharType"), "end")
            run._r.extend((field_begin, instruction, field_end))
            apply_run_font(run, self.config.font.name, self.config.font.size_pt)


def paragraph_alignment(alignment: Alignment):
    return _ALIGNMENTS[alignment]
