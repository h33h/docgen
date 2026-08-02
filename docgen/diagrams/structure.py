"""Structure diagram renderer."""

from pathlib import Path
import textwrap

import matplotlib.patches as patches
import matplotlib.pyplot as plt

from docgen.config.document import StructureFigure

from .base import save_figure
from .layout import apply_layout
from .registry import DiagramRegistry
from .validation import adjust_overlaps


@DiagramRegistry.register("structure")
def render_structure(resource: StructureFigure, output_dir: Path) -> Path:
    nodes = [node.model_dump() for node in resource.nodes]
    connections = [connection.model_dump(by_alias=True) for connection in resource.connections]
    nodes = apply_layout(nodes, connections, resource.options)
    if resource.options.adjust_overlaps:
        nodes = adjust_overlaps(nodes, resource.options.overlap_iterations, resource.options.minimum_padding)
    by_id = {node["id"]: node for node in nodes}

    figure, axes = plt.subplots(figsize=resource.options.figsize)
    for connection in connections:
        start, end = by_id[connection["from"]], by_id[connection["to"]]
        arrow = patches.FancyArrowPatch(
            (start["x"], start["y"]),
            (end["x"], end["y"]),
            arrowstyle="->",
            mutation_scale=15,
            linewidth=1.5,
            color="#34495e",
            zorder=1,
        )
        axes.add_patch(arrow)
        if connection.get("label"):
            axes.text(
                (start["x"] + end["x"]) / 2,
                (start["y"] + end["y"]) / 2,
                connection["label"],
                ha="center",
                va="center",
                fontsize=8,
                bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.8},
                zorder=3,
            )

    for node in nodes:
        if node["shape"] == "circle":
            shape = patches.Circle(
                (node["x"], node["y"]), node.get("size") or 0.10,
                facecolor=node["color"], edgecolor="black", alpha=0.8, zorder=2,
            )
        else:
            width = node.get("width") or node.get("size") or 0.18
            height = node.get("height") or node.get("size") or 0.10
            shape = patches.Rectangle(
                (node["x"] - width / 2, node["y"] - height / 2),
                width, height, facecolor=node["color"], edgecolor="black", alpha=0.8, zorder=2,
            )
        axes.add_patch(shape)
        axes.text(
            node["x"], node["y"], textwrap.fill(node["label"], width=18),
            ha="center", va="center", fontsize=node["font_size"], zorder=3,
        )

    margin = resource.options.bounds_margin
    axes.set_xlim(-margin, 1 + margin)
    axes.set_ylim(-margin, 1 + margin)
    axes.set_aspect("equal")
    axes.axis("off")
    if resource.title:
        axes.set_title(resource.title)
    figure.tight_layout()
    return save_figure(figure, resource, output_dir)
