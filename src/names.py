"""Проверка и нормализация имён пакетов."""

import re

from .errors import AppError

PACKAGE = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?")
TEST_PACKAGE = re.compile(r"[A-Z]+")


def normalize(name):
    """Привести имя PyPI к нижнему регистру с дефисами."""
    if not isinstance(name, str) or PACKAGE.fullmatch(name) is None:
        raise AppError(f"Некорректное имя пакета: {name!r}")
    return re.sub(r"[-_.]+", "-", name).lower()


def test_name(name):
    """Проверить обозначение тестового пакета большими буквами A–Z."""
    if not isinstance(name, str) or TEST_PACKAGE.fullmatch(name) is None:
        raise AppError("Тестовый пакет должен состоять из букв A–Z")
    return name
