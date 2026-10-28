"""Разбор имени, extras, ограничений версии и маркера Requires-Dist."""

from dataclasses import dataclass
import re

from .errors import AppError
from .names import normalize

HEAD = re.compile(r"([A-Za-z0-9][A-Za-z0-9._-]*)(?:\s*\[([^]]*)\])?(.*)")
SPECIFIER = re.compile(r"(?:===|~=|==|!=|<=|>=|<|>)\s*[-A-Za-z0-9.*+!_]+")


@dataclass(frozen=True)
class Requirement:
    """Объявленная зависимость с исходными ограничениями и условием."""

    name: str
    extras: frozenset = frozenset()
    specifier: str = ""
    marker: str = ""
    raw: str = ""


def _specifier(value):
    """Проверить синтаксис ограничений, не решая задачу установки версий."""
    value = value.strip()
    if value.startswith("(") and value.endswith(")"):
        value = value[1:-1].strip()
    if not value:
        return ""
    if value.startswith("@"):
        raise AppError("Прямые URL-зависимости не поддерживаются")
    for part in value.rstrip(",").split(","):
        if SPECIFIER.fullmatch(part.strip()) is None:
            raise AppError(f"Некорректное ограничение версии: {value}")
    return value


def parse_requirement(text):
    """Разобрать одну запись метаданных PyPI самостоятельно."""
    if not isinstance(text, str):
        raise AppError("Requires-Dist должен содержать строки")
    body, separator, marker = text.partition(";")
    match = HEAD.fullmatch(body.strip())
    if match is None:
        raise AppError(f"Неверная запись зависимости: {text!r}")
    name, extra_names, specifier = match.groups()
    extras = frozenset(normalize(x.strip()) for x in extra_names.split(",")) \
        if extra_names else frozenset()
    if separator and not marker.strip():
        raise AppError("После ; должно быть условие зависимости")
    return Requirement(normalize(name), extras, _specifier(specifier),
                       marker.strip(), text)
