"""Geometry helpers for structure diagrams."""

from __future__ import annotations

import copy
import math


def _bounds(node: dict):
    if node.get("shape") == "circle":
        radius = node.get("size") or 0.10
        return node["x"] - radius, node["x"] + radius, node["y"] - radius, node["y"] + radius
    width = node.get("width") or node.get("size") or 0.18
    height = node.get("height") or node.get("size") or 0.10
    return node["x"] - width / 2, node["x"] + width / 2, node["y"] - height / 2, node["y"] + height / 2


def find_overlaps(nodes: list[dict], padding: float = 0.02):
    overlaps = []
    for index, left in enumerate(nodes):
        lx1, lx2, ly1, ly2 = _bounds(left)
        for right in nodes[index + 1 :]:
            rx1, rx2, ry1, ry2 = _bounds(right)
            if lx2 + padding > rx1 and lx1 - padding < rx2 and ly2 + padding > ry1 and ly1 - padding < ry2:
                overlaps.append((left["id"], right["id"]))
    return overlaps


def adjust_overlaps(nodes: list[dict], iterations: int, padding: float):
    result = copy.deepcopy(nodes)
    by_id = {node["id"]: node for node in result}
    for _ in range(iterations):
        overlaps = find_overlaps(result, padding)
        if not overlaps:
            break
        for left_id, right_id in overlaps:
            left, right = by_id[left_id], by_id[right_id]
            dx, dy = right["x"] - left["x"], right["y"] - left["y"]
            distance = math.hypot(dx, dy)
            if distance < 0.001:
                dx, dy, distance = 1.0, 0.0, 1.0
            shift = padding
            left["x"] = max(0.05, min(0.95, left["x"] - shift * dx / distance))
            left["y"] = max(0.05, min(0.95, left["y"] - shift * dy / distance))
            right["x"] = max(0.05, min(0.95, right["x"] + shift * dx / distance))
            right["y"] = max(0.05, min(0.95, right["y"] + shift * dy / distance))
    return result
