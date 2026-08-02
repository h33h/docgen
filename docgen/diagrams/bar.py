"""Vertical and horizontal category charts."""

from pathlib import Path

import matplotlib.pyplot as plt

from docgen.config.document import BarFigure, HorizontalBarFigure

from .base import apply_axes_options, save_figure
from .registry import DiagramRegistry


@DiagramRegistry.register("bar")
def render_bar(resource: BarFigure, output_dir: Path) -> Path:
    figure, axes = plt.subplots(figsize=resource.options.figsize)
    bars = axes.bar(resource.labels, resource.values, color=resource.colors)
    apply_axes_options(axes, resource)
    if resource.options.show_values:
        axes.bar_label(bars, padding=3)
    figure.tight_layout()
    return save_figure(figure, resource, output_dir)


@DiagramRegistry.register("horizontal_bar")
def render_horizontal_bar(resource: HorizontalBarFigure, output_dir: Path) -> Path:
    figure, axes = plt.subplots(figsize=resource.options.figsize)
    bars = axes.barh(resource.labels, resource.values, color=resource.colors)
    apply_axes_options(axes, resource)
    if resource.options.show_values:
        axes.bar_label(bars, padding=3)
    figure.tight_layout()
    return save_figure(figure, resource, output_dir)
