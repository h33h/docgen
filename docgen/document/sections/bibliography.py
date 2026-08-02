"""Bibliography section based on first citation use."""

from docgen.config.document import BibliographySection, HeadingBlock, ParagraphBlock
from docgen.document.blocks import BlockRendererRegistry, RenderContext

from .base import SectionRendererRegistry


@SectionRendererRegistry.register("bibliography")
def render_bibliography(section: BibliographySection, context: RenderContext) -> None:
    if section.page_break_before:
        context.doc.add_page_break()
    if section.title:
        BlockRendererRegistry.render(
            HeadingBlock(type="heading", text=section.title, level=1), context
        )
    for number, reference in context.citations.used_entries():
        prefix = section.prefix.format(number=number)
        BlockRendererRegistry.render(
            ParagraphBlock(type="paragraph", text=f"{prefix}{reference.text}"), context
        )
