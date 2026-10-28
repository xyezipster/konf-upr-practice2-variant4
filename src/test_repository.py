"""Локальный тестовый репозиторий с пакетами A, B, C и т. д."""

import json
from pathlib import Path

from .errors import AppError
from .names import test_name
from .requirements import Requirement


def _validate(document):
    """Проверить обозначения пакетов, списки рёбер и наличие целей."""
    if not isinstance(document, dict):
        raise AppError("Тестовый репозиторий должен быть JSON-объектом")
    for name, dependencies in document.items():
        test_name(name)
        if not isinstance(dependencies, list):
            raise AppError(f"Зависимости {name} должны быть списком")
        for dependency in dependencies:
            test_name(dependency)
            if dependency not in document:
                raise AppError(f"Пакет {dependency} отсутствует в репозитории")
    return {name: sorted(set(deps)) for name, deps in document.items()}


class TestRepository:
    """Читать прямые зависимости из проверенного локального JSON."""

    def __init__(self, path):
        """Загрузить тестовые данные без сетевых запросов."""
        try:
            text = Path(path).read_text(encoding="utf-8")
            self.graph = _validate(json.loads(text))
        except (OSError, ValueError, UnicodeError) as error:
            raise AppError(f"Ошибка тестового репозитория: {error}") from error

    def dependencies(self, name, extras=()):
        """Получить требования для одного пакета или сообщить об ошибке."""
        if name not in self.graph:
            raise AppError(f"Тестовый пакет не найден: {name}")
        return tuple(Requirement(name=item, raw=item)
                     for item in self.graph[name])
