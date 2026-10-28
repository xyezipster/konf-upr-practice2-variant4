"""Построение графа зависимостей итеративным DFS."""

from .errors import AppError
from .requirements import Requirement


class GraphRepository:
    """Представить готовый словарь смежности как источник для DFS."""

    def __init__(self, graph):
        """Сохранить конечный граф без сетевых операций."""
        self.graph = graph

    def dependencies(self, name, extras=()):
        """Вернуть рёбра из вершины или сообщить об отсутствующем пакете."""
        if name not in self.graph:
            raise AppError(f"Пакет отсутствует в графе: {name}")
        return tuple(Requirement(item) for item in sorted(self.graph[name]))


def build_graph(package, source):
    """Обойти достижимые зависимости стеком, не используя рекурсию."""
    graph, expanded = {}, set()
    stack = [Requirement(package)]
    while stack:
        current = stack.pop()
        state = current.name, current.extras
        if state in expanded:
            continue
        expanded.add(state)
        dependencies = source.dependencies(current.name, current.extras)
        graph.setdefault(current.name, set())
        for dependency in reversed(dependencies):
            graph[current.name].add(dependency.name)
            graph.setdefault(dependency.name, set())
            stack.append(dependency)
    return graph


def format_graph(graph):
    """Показать все достижимые вершины и их прямые связи по алфавиту."""
    lines = []
    for name in sorted(graph):
        targets = ", ".join(sorted(graph[name])) or "(нет)"
        lines.append(f"{name}: {targets}")
    return "\n".join(lines)
