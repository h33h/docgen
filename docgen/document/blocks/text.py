"""Paragraph and heading blocks."""

from docgen.config.document import HeadingBlock, ParagraphBlock
from docgen.document.formatter import apply_run_font, paragraph_alignment

from .base import BlockRendererRegistry, RenderContext


@BlockRendererRegistry.register("paragraph")
def render_paragraph(block: ParagraphBlock, context: RenderContext) -> None:
    paragraph = context.doc.add_paragraph()
    paragraph.alignment = paragraph_alignment(block.alignment)
    if block.space_before_pt is not None:
        from docx.shared import Pt

        paragraph.paragraph_format.space_before = Pt(block.space_before_pt)
    if block.space_after_pt is not None:
        from docx.shared import Pt

        paragraph.paragraph_format.space_after = Pt(block.space_after_pt)
    run = paragraph.add_run(context.citations.replace(block.text))
    apply_run_font(
        run,
        context.config.formatting.font.name,
        context.config.formatting.font.size_pt,
        bold=block.bold,
        italic=block.italic,
    )


@BlockRendererRegistry.register("heading")
def render_heading(block: HeadingBlock, context: RenderContext) -> None:
    if block.include_in_toc:
        paragraph = context.doc.add_heading(level=block.level)
    else:
        paragraph = context.doc.add_paragraph()
    paragraph.alignment = paragraph_alignment(block.alignment)
    run = paragraph.add_run(block.text)
    apply_run_font(
        run,
        context.config.formatting.font.name,
        context.config.formatting.heading_sizes_pt[block.level],
        bold=True,
    )
