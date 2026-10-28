"""Чтение метаданных прямо из PyPI через стандартный urllib."""

import json
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from .errors import AppError
from .markers import applies
from .names import normalize
from .requirements import parse_requirement
from .tls import https_context

TIMEOUT = 15


def read_json(url):
    """Загрузить JSON по HTTP без менеджеров пакетов и внешних библиотек."""
    headers = {"Accept": "application/json",
               "User-Agent": "practice2-variant4/1.0"}
    request = Request(url, headers=headers)
    try:
        with urlopen(request, timeout=TIMEOUT,
                     context=https_context()) as response:
            return json.load(response)
    except HTTPError as error:
        error.close()
        raise AppError(f"Ошибка HTTP {error.code}: {url}") from error
    except (URLError, OSError, ValueError, UnicodeError) as error:
        raise AppError(f"Ошибка чтения репозитория {url}: {error}") from error


def _metadata(document, name):
    """Проверить обязательные поля и типы ответа PyPI."""
    if not isinstance(document, dict):
        raise AppError("Ответ PyPI должен быть JSON-объектом")
    if not isinstance(document.get("info"), dict):
        raise AppError("В ответе PyPI отсутствует объект info")
    info = document["info"]
    if normalize(info.get("name")) != name:
        raise AppError("Имя пакета в ответе PyPI не совпадает с запросом")
    if not isinstance(info.get("version"), str) or not info["version"]:
        raise AppError("В ответе PyPI отсутствует версия пакета")
    _validate_dependencies(info)
    return info


def _validate_dependencies(info):
    """Проверить наличие и тип списка зависимостей метаданных."""
    if "requires_dist" not in info:
        raise AppError("В ответе PyPI отсутствует поле requires_dist")
    dependencies = info["requires_dist"]
    dynamic = info.get("dynamic") or []
    if not isinstance(dynamic, list):
        raise AppError("dynamic должен быть списком или null")
    if dependencies is None and "requires_dist" in dynamic:
        raise AppError("PyPI не предоставил динамические зависимости пакета")
    if dependencies is not None and not isinstance(dependencies, list):
        raise AppError("requires_dist должен быть списком или null")


class PyPIRepository:
    """Получать прямые зависимости последней версии с кэшем в памяти."""

    def __init__(self, url, loader=None, values=None):
        """Сохранить URL источника, HTTP-загрузчик и окружение маркеров."""
        self.url = url.rstrip("/")
        self.loader = loader or read_json
        self.values = values
        self.cache = {}
        self.records = {}

    def _requirements(self, name):
        """Один раз загрузить и разобрать метаданные указанного пакета."""
        if name not in self.cache:
            url = f"{self.url}/pypi/{quote(name, safe='')}/json"
            info = _metadata(self.loader(url), name)
            self.records[name] = info
            self.cache[name] = tuple(parse_requirement(item)
                                     for item in info["requires_dist"] or [])
        return self.cache[name]

    def dependencies(self, name, extras=()):
        """Вернуть активные требования с учётом окружения и extras."""
        name = normalize(name)
        return tuple(item for item in self._requirements(name)
                     if applies(item.marker, extras, self.values))
