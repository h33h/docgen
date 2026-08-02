"""Word table-of-contents field section."""

from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from docgen.config.document import HeadingBlock, TocSection
from docgen.document.blocks import BlockRendererRegistry, RenderContext

from .base import SectionRendererRegistry


def _add_toc_field(context: RenderContext, minimum: int, maximum: int) -> None:
    paragraph = context.doc.add_paragraph()
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instruction = OxmlElement("w:instrText")
    instruction.set(qn("xml:space"), "preserve")
    instruction.text = f'TOC \\o "{minimum}-{maximum}" \\h \\z \\u'
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    placeholder = OxmlElement("w:t")
    placeholder.text = "Update this field in Word."
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend((begin, instruction, separate, placeholder, end))

    settings = context.doc.settings._element
    update = settings.find(qn("w:updateFields"))
    if update is None:
        update = OxmlElement("w:updateFields")
        settings.append(update)
    update.set(qn("w:val"), "true")


@SectionRendererRegistry.register("toc")
def render_toc(section: TocSection, context: RenderContext) -> None:
    if section.page_break_before:
        context.doc.add_page_break()
    if section.title:
        BlockRendererRegistry.render(
            HeadingBlock(type="heading", text=section.title, level=1, include_in_toc=False),
            context,
        )
    _add_toc_field(context, section.min_level, section.max_level)
