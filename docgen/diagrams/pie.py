"""Pie chart renderer."""

from pathlib import Path

import matplotlib.pyplot as plt

from docgen.config.document import PieFigure

from .base import save_figure
from .registry import DiagramRegistry


@DiagramRegistry.register("pie")
def render_pie(resource: PieFigure, output_dir: Path) -> Path:
    figure, axes = plt.subplots(figsize=resource.options.figsize)

    def percentage(value: float) -> str:
        if not resource.options.show_percentages or value < resource.options.minimum_label_percent:
            return ""
        return f"{value:.1f}%"

    axes.pie(
        resource.values,
        labels=resource.labels,
        colors=resource.colors,
        autopct=percentage,
        startangle=resource.options.start_angle,
    )
    if resource.title:
        axes.set_title(resource.title)
    axes.axis("equal")
    figure.tight_layout()
    return save_figure(figure, resource, output_dir)
