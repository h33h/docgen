"""Matplotlib helpers shared by chart renderers."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def save_figure(figure, resource, output_dir: Path) -> Path:
    output = output_dir / f"{resource.id}.png"
    try:
        figure.savefig(
            output,
            dpi=resource.options.dpi,
            bbox_inches="tight",
            facecolor="white",
        )
        return output
    finally:
        plt.close(figure)


def apply_axes_options(axes, resource) -> None:
    if resource.title:
        axes.set_title(resource.title)
    if getattr(resource.options, "xlabel", None):
        axes.set_xlabel(resource.options.xlabel)
    if getattr(resource.options, "ylabel", None):
        axes.set_ylabel(resource.options.ylabel)
    if getattr(resource.options, "grid", False):
        axes.grid(axis="y", alpha=0.3)
