"""Графы D2 и запуск итоговой версии отдельным процессом."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from src.d2 import format_d2

ROOT = Path(__file__).resolve().parents[1]


class D2Tests(unittest.TestCase):
    """Порядок вывода, циклы, пустые списки связей и сохранение файла."""

    def test_exact_diamond_output(self):
        output = format_d2({"B": {"C"}, "A": {"B", "C"}, "C": set()})
        self.assertEqual(output, 'direction: right\nn0: "A"\nn1: "B"\n'
                         'n2: "C"\nn0 -> n1\nn0 -> n2\nn1 -> n2\n')

    def test_self_loop_and_isolated(self):
        self.assertIn("n0 -> n0", format_d2({"A": {"A"}}))
        self.assertEqual(format_d2({"A": set()}),
                         'direction: right\nn0: "A"\n')

    def test_labels_are_escaped(self):
        text = format_d2({'a.b': {'a"b'}, 'a"b': set()})
        self.assertIn('a\\"b', text)
        self.assertEqual(text.count(" -> "), 1)

    def test_cli_writes_and_prints_d2(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/"nested"/"diagram.d2"
            result = subprocess.run([sys.executable, "-B", "main.py",
                                     "--output", str(path)], cwd=ROOT,
                                    text=True, capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(path.read_text(), result.stdout)
            self.assertEqual(result.stdout.count(" -> "), 4)

    def test_cli_reverse_d2(self):
        result = subprocess.run([sys.executable, "-B", "main.py",
                                 "--reverse", "D"], cwd=ROOT, text=True,
                                capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('"E"', result.stdout)

    def test_cli_unknown_package(self):
        result = subprocess.run([sys.executable, "-B", "main.py",
                                 "--reverse", "Z"], cwd=ROOT, text=True,
                                capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Ошибка:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
