"""Small neutral presentation themes."""

from dataclasses import dataclass

from pptx.dml.color import RGBColor


@dataclass(frozen=True)
class Theme:
    name: str
    background: RGBColor
    title_color: RGBColor
    text_color: RGBColor
    accent_color: RGBColor
    font_name: str


_THEMES = {
    "classic": Theme(
        name="classic",
        background=RGBColor(255, 255, 255),
        title_color=RGBColor(31, 41, 55),
        text_color=RGBColor(55, 65, 81),
        accent_color=RGBColor(37, 99, 235),
        font_name="Arial",
    ),
    "modern": Theme(
        name="modern",
        background=RGBColor(248, 250, 252),
        title_color=RGBColor(15, 23, 42),
        text_color=RGBColor(51, 65, 85),
        accent_color=RGBColor(14, 165, 233),
        font_name="Aptos",
    ),
}


def get_theme(name: str) -> Theme:
    try:
        return _THEMES[name]
    except KeyError as error:
        raise ValueError(f"unknown presentation theme: {name}") from error
