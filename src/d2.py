"""Детерминированный вывод графа на языке диаграмм D2."""

import json


def format_d2(graph):
    """Показать все вершины и связи, включая петли и циклы."""
    names = sorted(graph)
    identifiers = {name: f"n{index}" for index, name in enumerate(names)}
    lines = ["direction: right"]
    for name in names:
        label = json.dumps(name, ensure_ascii=False)
        lines.append(f"{identifiers[name]}: {label}")
    for name in names:
        for dependency in sorted(graph[name]):
            lines.append(f"{identifiers[name]} -> {identifiers[dependency]}")
    return "\n".join(lines) + "\n"
