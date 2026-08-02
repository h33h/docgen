"""Table resource block renderer."""

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm

from docgen.config.document import TableBlock
from docgen.document.formatter import apply_run_font
from docgen.document.resources import ResourceRegistry

from .base import BlockRendererRegistry, RenderContext


def _prevent_row_split(row) -> None:
    row_properties = row._tr.get_or_add_trPr()
    row_properties.append(OxmlElement("w:cantSplit"))


def _repeat_header(row) -> None:
    row_properties = row._tr.get_or_add_trPr()
    header = OxmlElement("w:tblHeader")
    header.set(qn("w:val"), "true")
    row_properties.append(header)


@BlockRendererRegistry.register("table")
def render_table(block: TableBlock, context: RenderContext) -> None:
    resource = ResourceRegistry(context.config.resources).table(block.ref)
    if resource.caption:
        caption = context.doc.add_paragraph(resource.caption)
        caption.alignment = WD_ALIGN_PARAGRAPH.CENTER

    row_count = len(resource.rows) + (1 if resource.headers is not None else 0)
    column_count = len(resource.headers) if resource.headers is not None else len(resource.rows[0])
    table = context.doc.add_table(rows=row_count, cols=column_count)
    table.style = "Table Grid"
    table.autofit = resource.column_widths_cm is None

    values = ([resource.headers] if resource.headers is not None else []) + resource.rows
    for row_index, values_row in enumerate(values):
        row = table.rows[row_index]
        _prevent_row_split(row)
        if row_index == 0 and resource.headers is not None:
            _repeat_header(row)
        for column_index, value in enumerate(values_row):
            cell = row.cells[column_index]
            cell.text = value
            if resource.column_widths_cm is not None:
                cell.width = Cm(resource.column_widths_cm[column_index])
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    apply_run_font(
                        run,
                        context.config.formatting.font.name,
                        context.config.formatting.font.size_pt,
                        bold=row_index == 0 and resource.headers is not None,
                    )
