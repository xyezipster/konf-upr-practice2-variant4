"""Разбор Requires-Dist, маркеры и данные репозитория."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from src.errors import AppError
from src.markers import applies
from src.repository import PyPIRepository, read_json
from src.requirements import parse_requirement
from src.test_repository import TestRepository


class RequirementTests(unittest.TestCase):
    """Имена, версии, extras и ошибочные строки метаданных."""

    def test_normalize_and_preserve(self):
        item = parse_requirement('Some_Pkg[CLI,fast] (>=1.0,<3); extra=="x"')
        self.assertEqual(item.name, "some-pkg")
        self.assertEqual(item.extras, frozenset({"cli", "fast"}))
        self.assertEqual(item.specifier, ">=1.0,<3")
        self.assertEqual(item.marker, 'extra=="x"')

    def test_invalid(self):
        for text in [None, "", "x>=", "x nonsense", "x;", "x @ https://x"]:
            with self.subTest(text=text), self.assertRaises(AppError):
                parse_requirement(text)


class MarkerTests(unittest.TestCase):
    """Условия окружения, приоритет операций и дополнительные группы."""

    def setUp(self):
        self.values = {"python_version": "3.14", "sys_platform": "darwin",
                       "python_full_version": "3.14.0", "extra": ""}

    def check(self, text, expected):
        self.assertEqual(applies(text, values=self.values), expected)

    def test_version_order(self):
        self.check('python_version >= "3.9"', True)
        self.check('python_version < "3.11"', False)
        self.check('python_version == "3.14.*"', True)
        self.check('python_full_version >= "3.14.0rc1"', True)
        self.check('python_version ~= "3.13"', True)

    def test_boolean_and_parentheses(self):
        self.check('python_version < "3.11" or sys_platform == "darwin"',
                   True)
        self.check('(python_version >= "3.11" and sys_platform == "win32")'
                   ' or python_version < "3.0"', False)
        self.check('"darwin" == sys_platform', True)

    def test_membership(self):
        self.check('sys_platform in "darwin,linux"', True)
        self.check('sys_platform not in "win32"', True)

    def test_extras(self):
        marker = 'extra == "socks"'
        self.assertFalse(applies(marker, values=self.values))
        self.assertTrue(applies(marker, ("security", "socks"), self.values))

    def test_invalid(self):
        for marker in ['unknown == "x"', 'extra ==', '(extra == "x"',
                       'extra == "x" junk', 'extra not "x"', 'extra + "x"']:
            with self.subTest(marker=marker), self.assertRaises(AppError):
                applies(marker, values=self.values)


class RepositoryTests(unittest.TestCase):
    """Кэш, корректность ответа PyPI и обработка ошибок HTTP."""

    def test_direct_dependencies_and_cache(self):
        calls = []

        def loader(url):
            calls.append(url)
            return {"info": {"name": "demo", "version": "1.0",
                             "requires_dist": ["base>=1", 'socks;extra=="x"']}}
        source = PyPIRepository("https://pypi.org", loader=loader)
        self.assertEqual([x.name for x in source.dependencies("demo")],
                         ["base"])
        self.assertEqual(len(source.dependencies("demo", ("x",))), 2)
        self.assertEqual(calls, ["https://pypi.org/pypi/demo/json"])

    def test_empty_and_invalid_metadata(self):
        valid = {"name": "demo", "version": "1", "requires_dist": None,
                 "dynamic": None}
        source = PyPIRepository("https://pypi.org",
                                loader=lambda url: {"info": valid})
        self.assertEqual(source.dependencies("demo"), ())
        for item in [{}, {"info": []}, {"info": {**valid, "name": "other"}},
                     {"info": {**valid, "requires_dist": "bad"}},
                     {"info": {**valid, "dynamic": "bad"}},
                     {"info": {**valid, "dynamic": ["requires_dist"]}}]:
            source = PyPIRepository("https://pypi.org", loader=lambda url: item)
            with self.subTest(item=item), self.assertRaises(AppError):
                source.dependencies("demo")

    def test_http_errors(self):
        errors = [HTTPError("https://x", 404, "missing", {}, None),
                  URLError("offline"), TimeoutError("timeout")]
        for error in errors:
            with self.subTest(error=error), patch("src.repository.urlopen",
                                                  side_effect=error):
                with self.assertRaises(AppError):
                    read_json("https://pypi.org/pypi/missing/json")

    def test_local_repository_errors(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/"graph.json"
            for data in [[], {"a": []}, {"A": ["B"]}, {"A": "B"}]:
                path.write_text(json.dumps(data))
                with self.subTest(data=data), self.assertRaises(AppError):
                    TestRepository(path)

    def test_local_repository_deduplicates(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/"graph.json"
            path.write_text('{"A":["B","B"],"B":[]}')
            source = TestRepository(path)
            self.assertEqual([x.name for x in source.dependencies("A")], ["B"])
            with self.assertRaises(AppError):
                source.dependencies("Z")
