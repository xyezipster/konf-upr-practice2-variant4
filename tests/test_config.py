"""Ошибки конфигурации и способы запуска приложения."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from src.config import load_config
from src.errors import AppError

ROOT = Path(__file__).resolve().parents[1]


class ConfigTests(unittest.TestCase):
    """Проверка каждого настраиваемого параметра."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name).resolve()
        (self.folder / "repo.json").write_text('{"A": []}')
        self.path = self.folder / "config.toml"

    def load(self, text):
        self.path.write_text(text, encoding="utf-8")
        return load_config(self.path)

    def test_local_config(self):
        config = self.load('package="A"\nrepository="repo.json"\n'
                           'test_mode=true\n')
        self.assertEqual(config.package, "A")
        self.assertEqual(config.repository, str(self.folder / "repo.json"))
        self.assertIn("test_mode=true", config.describe())

    def test_remote_name_normalization(self):
        config = self.load('package="Some_Package"\n'
                           'repository="https://pypi.org/"\n'
                           'test_mode=false\n')
        self.assertEqual(config.package, "some-package")
        self.assertEqual(config.repository, "https://pypi.org")

    def test_invalid_parameters(self):
        base = 'package={name}\nrepository={source}\ntest_mode={mode}\n'
        cases = [('""', '"repo.json"', 'true'),
                 ('1', '"repo.json"', 'true'),
                 ('"a"', '"repo.json"', 'true'),
                 ('"A"', '"missing.json"', 'true'),
                 ('"A"', '[]', 'true'),
                 ('"A"', '"repo.json"', '"true"'),
                 ('"x"', '"not-url"', 'false'),
                 ('"x"', '"https://["', 'false'),
                 ('"x"', '"https://github.com"', 'false')]
        for name, source, mode in cases:
            with self.subTest(name=name, source=source, mode=mode):
                with self.assertRaises(AppError):
                    self.load(base.format(name=name, source=source, mode=mode))

    def test_missing_unknown_and_broken_fields(self):
        for text in ['package="A"', 'bad=[',
                     'package="A"\nrepository="repo.json"\n'
                     'test_mode=true\nother=1']:
            with self.subTest(text=text), self.assertRaises(AppError):
                self.load(text)

    def test_missing_config(self):
        with self.assertRaises(AppError):
            load_config(self.folder / "missing.toml")

    def test_direct_launch_from_another_directory(self):
        result = subprocess.run([sys.executable, "-B", str(ROOT / "main.py")],
                                cwd=self.folder, capture_output=True,
                                text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("package=A", result.stdout)

    def test_module_launch(self):
        result = subprocess.run([sys.executable, "-B", "-m", "src"], cwd=ROOT,
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("package=A", result.stdout)
