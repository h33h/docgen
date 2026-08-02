from pathlib import Path

import matplotlib.pyplot as plt
from pptx import Presentation

from docgen.config.document import TableResource
from docgen.presentation.slides import SlideFactory
from docgen.presentation.themes import get_theme


def slide_text(slide):
    return "\n".join(
        shape.text for shape in slide.shapes if hasattr(shape, "text") and shape.text
    )


def test_slide_factory_renders_all_generic_layouts(tmp_path: Path):
    image = tmp_path / "figure.png"
    figure, axes = plt.subplots(figsize=(1, 1))
    axes.plot([0, 1], [0, 1])
    figure.savefig(image)
    plt.close(figure)

    presentation = Presentation()
    factory = SlideFactory(presentation, get_theme("classic"))
    factory.add_title_slide("Title", "Subtitle", "Author", ["Line"])
    factory.add_contents_slide("Contents", ["One", "Two"])
    factory.add_text_slide("Text", "Body", "Subtitle")
    factory.add_bullets_slide("Bullets", ["One", "Two"])
    factory.add_two_column_slide("Compare", ["Left"], ["Right"], "L", "R")
    factory.add_table_slide(
        "Table",
        TableResource(id="table", headers=["A"], rows=[["1"]]),
    )
    factory.add_figure_slide("Figure", image, "Caption")
    factory.add_sources_slide("Sources", ["Source"])
    factory.add_thanks_slide("Thank you", "Questions")

    assert len(presentation.slides) == 9
    assert "Title" in slide_text(presentation.slides[0])
    assert "Author" in slide_text(presentation.slides[0])
    assert "Body" in slide_text(presentation.slides[2])
    assert "Left" in slide_text(presentation.slides[4])
    assert len(presentation.slides[5].shapes) >= 2
    assert any(shape.shape_type == 13 for shape in presentation.slides[6].shapes)


def test_theme_names_are_strict():
    assert get_theme("classic").name == "classic"
    assert get_theme("modern").name == "modern"
    try:
        get_theme("unsupported")
    except ValueError as error:
        assert "unknown presentation theme" in str(error)
    else:
        raise AssertionError("unknown theme name must fail")
