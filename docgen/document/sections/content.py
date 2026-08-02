"""Generic content section."""

from docgen.config.document import ContentSection, HeadingBlock
from docgen.document.blocks import BlockRendererRegistry, RenderContext

from .base import SectionRendererRegistry


@SectionRendererRegistry.register("content")
def render_content(section: ContentSection, context: RenderContext) -> None:
    if section.page_break_before:
        context.doc.add_page_break()
    if section.title:
        BlockRendererRegistry.render(
            HeadingBlock(
                type="heading",
                text=section.title,
                level=section.level,
                include_in_toc=section.include_in_toc,
            ),
            context,
        )
    for block in section.content or []:
        BlockRendererRegistry.render(block, context)
