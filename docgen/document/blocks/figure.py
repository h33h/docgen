"""Image and chart figure block renderer."""

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches

from docgen.config.document import FigureBlock, ImageFigure
from docgen.document.formatter import apply_run_font
from docgen.document.resources import ResourceRegistry

from .base import BlockRendererRegistry, RenderContext


@BlockRendererRegistry.register("figure")
def render_figure(block: FigureBlock, context: RenderContext) -> None:
    resource = ResourceRegistry(context.config.resources).figure(block.ref)
    if isinstance(resource, ImageFigure):
        image_path = resource.path
    else:
        if context.temp_dir is None:
            raise RuntimeError("diagram rendering requires a temporary directory")
        from docgen.diagrams import DiagramRegistry

        image_path = DiagramRegistry.render(resource, context.temp_dir)

    paragraph = context.doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    width = block.width_inches or resource.width_inches
    paragraph.add_run().add_picture(str(image_path), width=Inches(width))
    if resource.caption:
        caption = context.doc.add_paragraph()
        caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = caption.add_run(resource.caption)
        apply_run_font(
            run,
            context.config.formatting.font.name,
            context.config.formatting.font.size_pt,
        )
