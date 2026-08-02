"""Bullet and numbered list blocks."""

from docx.oxml.ns import qn

from docgen.config.document import BulletListBlock, NumberedListBlock
from docgen.document.formatter import apply_run_font

from .base import BlockRendererRegistry, RenderContext


def _style_for(prefix: str, level: int) -> str:
    if level == 0:
        return prefix
    return f"{prefix} {min(level + 1, 3)}"


def _numbering_abstract_id(context: RenderContext, style_name: str) -> int:
    numbering = context.doc.part.numbering_part.element
    for abstract in numbering.findall(qn("w:abstractNum")):
        styles = [item.get(qn("w:val")) for item in abstract.iter(qn("w:pStyle"))]
        if style_name.replace(" ", "") in styles:
            return int(abstract.get(qn("w:abstractNumId")))
    raise RuntimeError(f"numbering style not found: {style_name}")


def _new_numbering(context: RenderContext, style_name: str, level: int, start: int) -> int:
    numbering = context.doc.part.numbering_part.element
    abstract_id = _numbering_abstract_id(context, style_name)
    number = numbering.add_num(abstract_id)
    override = number.add_lvlOverride(ilvl=level)
    override.add_startOverride(start)
    return int(number.numId)


def _apply_num_id(paragraph, num_id: int, level: int) -> None:
    num_pr = paragraph._p.get_or_add_pPr().get_or_add_numPr()
    num_pr.get_or_add_ilvl().val = level
    num_pr.get_or_add_numId().val = num_id


def _add_list_item(context: RenderContext, text: str, style: str):
    paragraph = context.doc.add_paragraph(style=style)
    run = paragraph.add_run(context.citations.replace(text))
    apply_run_font(
        run,
        context.config.formatting.font.name,
        context.config.formatting.font.size_pt,
    )
    return paragraph


@BlockRendererRegistry.register("bullet_list")
def render_bullet_list(block: BulletListBlock, context: RenderContext) -> None:
    style = _style_for("List Bullet", block.level)
    for item in block.items:
        _add_list_item(context, item, style)


@BlockRendererRegistry.register("numbered_list")
def render_numbered_list(block: NumberedListBlock, context: RenderContext) -> None:
    style = _style_for("List Number", block.level)
    num_id = _new_numbering(context, style, block.level, block.start)
    for item in block.items:
        paragraph = _add_list_item(context, item, style)
        _apply_num_id(paragraph, num_id, block.level)
