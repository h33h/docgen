"""Deterministic layouts for structure diagrams."""

from __future__ import annotations

from collections import defaultdict, deque
import copy
import math
import random

from docgen.config.document import StructureOptions


def _roots(nodes: list[dict], connections: list[dict]) -> list[str]:
    ids = [node["id"] for node in nodes]
    incoming = {connection["to"] for connection in connections}
    roots = [node_id for node_id in ids if node_id not in incoming]
    return roots or ids[:1]


def tree_layout(nodes: list[dict], connections: list[dict], options: StructureOptions):
    adjacency: dict[str, list[str]] = defaultdict(list)
    for connection in connections:
        adjacency[connection["from"]].append(connection["to"])
    levels: dict[int, list[str]] = defaultdict(list)
    visited: set[str] = set()
    queue = deque((node_id, 0) for node_id in _roots(nodes, connections))
    while queue:
        node_id, level = queue.popleft()
        if node_id in visited:
            continue
        visited.add(node_id)
        levels[level].append(node_id)
        queue.extend((child, level + 1) for child in adjacency[node_id])
    final_level = max(levels, default=0) + 1
    levels[final_level].extend(node["id"] for node in nodes if node["id"] not in visited)

    positions = {}
    for level, ids in levels.items():
        for index, node_id in enumerate(ids):
            offset = (index - (len(ids) - 1) / 2) * options.node_spacing
            if options.layout_direction == "TB":
                positions[node_id] = {"x": 0.5 + offset, "y": 0.9 - level * options.level_spacing}
            else:
                positions[node_id] = {"x": 0.1 + level * options.level_spacing, "y": 0.5 - offset}
    return positions


def grid_layout(nodes: list[dict], options: StructureOptions):
    columns = options.grid_columns or max(1, math.ceil(math.sqrt(len(nodes))))
    positions = {}
    for index, node in enumerate(nodes):
        row, column = divmod(index, columns)
        positions[node["id"]] = {
            "x": 0.5 + (column - (columns - 1) / 2) * options.node_spacing,
            "y": 0.9 - row * options.node_spacing,
        }
    return positions


def force_layout(nodes: list[dict], connections: list[dict], options: StructureOptions):
    random.seed(42)
    positions = {}
    for index, node in enumerate(nodes):
        angle = 2 * math.pi * index / len(nodes)
        positions[node["id"]] = {"x": 0.5 + 0.3 * math.cos(angle), "y": 0.5 + 0.3 * math.sin(angle)}
    ids = [node["id"] for node in nodes]
    edges = [(edge["from"], edge["to"]) for edge in connections]
    for iteration in range(options.force_iterations):
        forces = {node_id: [0.0, 0.0] for node_id in ids}
        for index, left in enumerate(ids):
            for right in ids[index + 1 :]:
                dx = positions[right]["x"] - positions[left]["x"]
                dy = positions[right]["y"] - positions[left]["y"]
                distance = math.hypot(dx, dy) + 0.001
                force = options.force_repulsion / distance**2
                fx, fy = force * dx / distance, force * dy / distance
                forces[left][0] -= fx
                forces[left][1] -= fy
                forces[right][0] += fx
                forces[right][1] += fy
        for left, right in edges:
            dx = positions[right]["x"] - positions[left]["x"]
            dy = positions[right]["y"] - positions[left]["y"]
            distance = math.hypot(dx, dy) + 0.001
            force = (distance - options.force_k) * 0.5
            fx, fy = force * dx / distance, force * dy / distance
            forces[left][0] += fx
            forces[left][1] += fy
            forces[right][0] -= fx
            forces[right][1] -= fy
        damping = 0.9 * (1 - iteration / options.force_iterations)
        for node_id in ids:
            positions[node_id]["x"] = max(0.05, min(0.95, positions[node_id]["x"] + forces[node_id][0] * damping))
            positions[node_id]["y"] = max(0.05, min(0.95, positions[node_id]["y"] + forces[node_id][1] * damping))
    return positions


def apply_layout(nodes: list[dict], connections: list[dict], options: StructureOptions):
    result = copy.deepcopy(nodes)
    if options.layout == "manual":
        return result
    if options.layout == "tree":
        positions = tree_layout(result, connections, options)
    elif options.layout == "grid":
        positions = grid_layout(result, options)
    else:
        positions = force_layout(result, connections, options)
    for node in result:
        node.update(positions[node["id"]])
    return result
