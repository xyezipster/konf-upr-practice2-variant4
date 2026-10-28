"""Обратные зависимости на всём тестовом репозитории."""

import unittest

from src.errors import AppError
from src.graph import GraphRepository, reverse_dependencies, reverse_graph


class ReverseTests(unittest.TestCase):
    """Прямые и транзитивные предки, включая недостижимые из корня."""

    def test_all_ancestors_in_test_repository(self):
        source = GraphRepository({"A": ["B", "C"], "B": ["D"],
                                  "C": ["D"], "D": [], "E": ["C"]})
        graph = reverse_dependencies("A", "D", source)
        self.assertEqual(set(graph), {"A", "B", "C", "D", "E"})
        self.assertEqual(graph["D"], {"B", "C"})
        self.assertEqual(graph["C"], {"A", "E"})

    def test_reverse_cycle(self):
        source = GraphRepository({"A": ["B"], "B": ["A"]})
        self.assertEqual(reverse_dependencies("A", "A", source),
                         {"A": {"B"}, "B": {"A"}})

    def test_no_reverse_dependencies(self):
        source = GraphRepository({"A": [], "B": ["A"]})
        self.assertEqual(reverse_dependencies("A", "B", source),
                         {"B": set()})

    def test_unknown_target(self):
        with self.assertRaises(AppError):
            reverse_dependencies("A", "Z", GraphRepository({"A": []}))

    def test_reverse_is_involution(self):
        graph = {"A": {"B"}, "B": set(), "C": {"A", "B"}}
        self.assertEqual(reverse_graph(reverse_graph(graph)), graph)
