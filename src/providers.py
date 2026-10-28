"""Выбор источника зависимостей по конфигурации."""

from .repository import PyPIRepository
from .test_repository import TestRepository


def repository(config):
    """Создать HTTP-источник PyPI либо локальный тестовый репозиторий."""
    return (TestRepository(config.repository) if config.test_mode
            else PyPIRepository(config.repository))
