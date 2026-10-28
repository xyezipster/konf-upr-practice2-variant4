"""Чтение и проверка TOML-конфигурации."""

from dataclasses import dataclass
from pathlib import Path
import tomllib
from urllib.parse import urlsplit

from .errors import AppError
from .names import normalize, test_name

FIELDS = {"package", "repository", "test_mode"}
FORBIDDEN_HOSTS = {"github.com", "raw.githubusercontent.com", "api.github.com"}


@dataclass(frozen=True)
class Config:
    """Имя пакета, источник данных и признак тестового режима."""

    package: str
    repository: str
    test_mode: bool

    def describe(self):
        """Вернуть параметры в формате ключ=значение для первого этапа."""
        mode = str(self.test_mode).lower()
        return (f"package={self.package}\nrepository={self.repository}\n"
                f"test_mode={mode}")


def _fields(data):
    """Проверить обязательные поля и их типы."""
    if set(data) != FIELDS:
        raise AppError("В TOML нужны только package, repository, test_mode")
    if type(data["test_mode"]) is not bool:
        raise AppError("test_mode должен быть true или false")
    for key in ("package", "repository"):
        if not isinstance(data[key], str) or not data[key].strip():
            raise AppError(f"{key} должен быть непустой строкой")


def _source(value, test_mode, folder):
    """Проверить локальный файл или адрес репозитория PyPI JSON API."""
    if test_mode:
        path = (folder / value).resolve()
        if not path.is_file():
            raise AppError(f"Файл тестового репозитория не найден: {path}")
        return str(path)
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise AppError("repository должен быть URL http:// или https://")
    if parsed.hostname.lower() in FORBIDDEN_HOSTS:
        raise AppError("GitHub нельзя использовать как источник зависимостей")
    if parsed.query or parsed.fragment:
        raise AppError("URL репозитория не должен содержать query или fragment")
    return value.rstrip("/")


def load_config(path):
    """Загрузить TOML; относительный путь источника считать от TOML-файла."""
    path = Path(path).resolve()
    try:
        with path.open("rb") as stream:
            data = tomllib.load(stream)
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise AppError(f"Ошибка чтения конфигурации {path}: {error}") from error
    _fields(data)
    mode = data["test_mode"]
    package = test_name(data["package"]) if mode else normalize(data["package"])
    repository = _source(data["repository"], mode, path.parent)
    return Config(package, repository, mode)
