"""Page break block."""

from docgen.config.document import PageBreakBlock

from .base import BlockRendererRegistry, RenderContext


@BlockRendererRegistry.register("page_break")
def render_page_break(block: PageBreakBlock, context: RenderContext) -> None:
    context.doc.add_page_break()
