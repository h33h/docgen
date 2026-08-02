"""Generic PowerPoint slide layouts."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from pptx import Presentation
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

from docgen.config.document import TableResource

from .themes import Theme


class SlideFactory:
    def __init__(self, presentation: Presentation, theme: Theme):
        self.prs = presentation
        self.theme = theme
        self.prs.slide_width = Inches(13.333)
        self.prs.slide_height = Inches(7.5)

    def _blank(self):
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        background = slide.background.fill
        background.solid()
        background.fore_color.rgb = self.theme.background
        return slide

    def _textbox(
        self,
        slide,
        text: str,
        left: float,
        top: float,
        width: float,
        height: float,
        *,
        size: float = 24,
        bold: bool = False,
        center: bool = False,
        color=None,
    ):
        shape = slide.shapes.add_textbox(
            Inches(left), Inches(top), Inches(width), Inches(height)
        )
        frame = shape.text_frame
        frame.word_wrap = True
        paragraph = frame.paragraphs[0]
        paragraph.text = text
        paragraph.font.name = self.theme.font_name
        paragraph.font.size = Pt(size)
        paragraph.font.bold = bold
        paragraph.font.color.rgb = color or self.theme.text_color
        if center:
            paragraph.alignment = PP_ALIGN.CENTER
        return shape

    def _title(self, slide, title: str):
        return self._textbox(
            slide,
            title,
            0.8,
            0.35,
            11.7,
            0.8,
            size=30,
            bold=True,
            center=True,
            color=self.theme.title_color,
        )

    def _items(self, slide, items: Iterable[str], left=1.1, top=1.7, width=11.1):
        shape = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(4.8))
        frame = shape.text_frame
        frame.clear()
        for index, item in enumerate(items):
            paragraph = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
            paragraph.text = f"• {item}"
            paragraph.font.name = self.theme.font_name
            paragraph.font.size = Pt(22)
            paragraph.font.color.rgb = self.theme.text_color
            paragraph.space_after = Pt(10)
        return shape

    def add_title_slide(self, title, subtitle=None, author=None, lines=()):
        slide = self._blank()
        self._textbox(
            slide, title, 1.0, 1.5, 11.3, 1.5,
            size=38, bold=True, center=True, color=self.theme.title_color,
        )
        details = [value for value in (subtitle, author, *lines) if value]
        if details:
            self._textbox(slide, "\n".join(details), 1.5, 3.4, 10.3, 2.0, size=21, center=True)
        return slide

    def add_contents_slide(self, title, items):
        slide = self._blank()
        self._title(slide, title)
        self._items(slide, items)
        return slide

    def add_text_slide(self, title, text, subtitle=None):
        slide = self._blank()
        self._title(slide, title)
        top = 1.35
        if subtitle:
            self._textbox(slide, subtitle, 1.0, top, 11.3, 0.5, size=18, center=True)
            top = 2.0
        self._textbox(slide, text, 1.0, top, 11.3, 4.8, size=22)
        return slide

    def add_bullets_slide(self, title, items, subtitle=None):
        slide = self._blank()
        self._title(slide, title)
        if subtitle:
            self._textbox(slide, subtitle, 1.0, 1.25, 11.3, 0.45, size=18, center=True)
        self._items(slide, items, top=1.8 if subtitle else 1.5)
        return slide

    def add_two_column_slide(self, title, left, right, left_title=None, right_title=None):
        slide = self._blank()
        self._title(slide, title)
        if left_title:
            self._textbox(slide, left_title, 0.7, 1.35, 5.8, 0.5, size=20, bold=True, center=True)
        if right_title:
            self._textbox(slide, right_title, 6.8, 1.35, 5.8, 0.5, size=20, bold=True, center=True)
        self._items(slide, left, left=0.8, top=1.9, width=5.6)
        self._items(slide, right, left=6.9, top=1.9, width=5.6)
        return slide

    def add_table_slide(self, title, table_resource: TableResource):
        slide = self._blank()
        self._title(slide, title)
        rows = len(table_resource.rows) + (1 if table_resource.headers else 0)
        columns = len(table_resource.headers or table_resource.rows[0])
        shape = slide.shapes.add_table(rows, columns, Inches(0.8), Inches(1.5), Inches(11.7), Inches(5.2))
        values = ([table_resource.headers] if table_resource.headers else []) + table_resource.rows
        for row_index, row in enumerate(values):
            for column_index, value in enumerate(row):
                cell = shape.table.cell(row_index, column_index)
                cell.text = value
                for paragraph in cell.text_frame.paragraphs:
                    paragraph.font.name = self.theme.font_name
                    paragraph.font.size = Pt(16)
                    paragraph.font.bold = row_index == 0 and table_resource.headers is not None
        return slide

    def add_figure_slide(self, title, image_path: Path, caption=None):
        slide = self._blank()
        self._title(slide, title)
        slide.shapes.add_picture(str(image_path), Inches(2.0), Inches(1.4), width=Inches(9.3), height=Inches(4.9))
        if caption:
            self._textbox(slide, caption, 1.0, 6.45, 11.3, 0.4, size=15, center=True)
        return slide

    def add_sources_slide(self, title, items):
        return self.add_bullets_slide(title, items)

    def add_thanks_slide(self, title, subtitle=None):
        slide = self._blank()
        self._textbox(
            slide, title, 1.0, 2.4, 11.3, 1.2,
            size=40, bold=True, center=True, color=self.theme.title_color,
        )
        if subtitle:
            self._textbox(slide, subtitle, 1.0, 4.0, 11.3, 0.8, size=22, center=True)
        return slide
