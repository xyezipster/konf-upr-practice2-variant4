"""Транзитивные связи, DFS, циклы, повторы и дополнительные группы."""

import unittest

from src.errors import AppError
from src.graph import GraphRepository, build_graph
from src.repository import PyPIRepository


class CountingRepository(GraphRepository):
    """Считать раскрытия вершин тестового графа."""

    def __init__(self, graph):
        super().__init__(graph)
        self.calls = []

    def dependencies(self, name, extras=()):
        self.calls.append(name)
        return super().dependencies(name, extras)


class GraphTests(unittest.TestCase):
    """Каждая связь учитывается, циклы не приводят к зависанию."""

    def test_diamond_and_dfs_order(self):
        source = CountingRepository({"A": ["B", "C"], "B": ["D"],
                                     "C": ["D"], "D": []})
        graph = build_graph("A", source)
        self.assertEqual(graph["A"], {"B", "C"})
        self.assertEqual(graph["B"], {"D"})
        self.assertEqual(source.calls, ["A", "B", "D", "C"])

    def test_cycle(self):
        source = CountingRepository({"A": ["B"], "B": ["C"], "C": ["A"]})
        graph = build_graph("A", source)
        self.assertEqual(graph["C"], {"A"})
        self.assertEqual(len(source.calls), 3)

    def test_self_loop(self):
        self.assertEqual(build_graph("A", GraphRepository({"A": ["A"]})),
                         {"A": {"A"}})

    def test_isolated_and_unreachable(self):
        graph = build_graph("A", GraphRepository({"A": [], "B": []}))
        self.assertEqual(graph, {"A": set()})

    def test_depth_exceeds_recursion_limit(self):
        size = 2000
        graph = {str(i): [str(i + 1)] for i in range(size)}
        graph[str(size)] = []
        self.assertEqual(len(build_graph("0", GraphRepository(graph))),
                         size + 1)

    def test_missing_node(self):
        with self.assertRaises(AppError):
            build_graph("Z", GraphRepository({"A": []}))

    def test_extras_from_different_paths(self):
        requirements = {"a": ["b[foo]", "c"], "c": ["b[bar]"],
                        "b": ['x;extra=="foo"', 'y;extra=="bar"'],
                        "x": [], "y": []}
        calls = []

        def loader(url):
            name = url.split("/")[-2]
            calls.append(name)
            return {"info": {"name": name, "version": "1",
                             "requires_dist": requirements[name]}}

        source = PyPIRepository("https://example.test", loader=loader)
        graph = build_graph("a", source)
        self.assertEqual(graph["b"], {"x", "y"})
        self.assertEqual(calls.count("b"), 1)
