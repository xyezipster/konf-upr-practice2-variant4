"""Сравнение версий в условиях Requires-Dist без сторонних библиотек."""

from itertools import zip_longest
import operator
import re

from .errors import AppError

VERSION = re.compile(
    r"(?:(\d+)!)?(\d+(?:\.\d+)*)"
    r"(?:(a|b|rc)(\d*))?(?:\.post(\d+))?(?:\.dev(\d+))?"
    r"(?:\+[a-z0-9.]+)?", re.IGNORECASE)
PRE = {"a": 0, "b": 1, "rc": 2}
FINAL = 3
COMPARISONS = {"==": operator.eq, "!=": operator.ne, ">": operator.gt,
               ">=": operator.ge, "<": operator.lt, "<=": operator.le}


def _parts(text):
    """Разобрать epoch, release, pre, post и dev распространённых версий."""
    match = VERSION.fullmatch(text)
    if match is None:
        raise AppError(f"Неподдерживаемая версия в условии: {text}")
    epoch, release, pre, number, post, dev = match.groups()
    phase = (PRE[pre.lower()], int(number or 0)) if pre else (FINAL, 0)
    if dev is not None and pre is None and post is None:
        phase = (-1, 0)
    tail = (phase, int(post) if post is not None else -1,
            int(dev) if dev is not None else float("inf"))
    return int(epoch or 0), tuple(map(int, release.split("."))), tail


def _ordered(left, right):
    """Подготовить сравнимые ключи с выравниванием release нулями."""
    lepoch, lrelease, ltail = _parts(left)
    repoch, rrelease, rtail = _parts(right)
    pairs = list(zip_longest(lrelease, rrelease, fillvalue=0))
    return ((lepoch, tuple(a for a, _ in pairs), ltail),
            (repoch, tuple(b for _, b in pairs), rtail))


def version_compare(left, operation, right):
    """Сравнить версии, включая == X.* и совместимый диапазон ~= X.Y."""
    if right.endswith(".*") and operation in {"==", "!="}:
        prefix = _parts(right[:-2])[1]
        matched = _parts(left)[1][:len(prefix)] == prefix
        return matched if operation == "==" else not matched
    if operation == "~=":
        release = _parts(right)[1]
        if len(release) < 2:
            raise AppError("После ~= нужна версия минимум из двух чисел")
        prefix = release[:-1]
        return (version_compare(left, ">=", right)
                and _parts(left)[1][:len(prefix)] == prefix)
    if operation not in COMPARISONS:
        raise AppError(f"Неизвестная операция сравнения: {operation}")
    first, second = _ordered(left, right)
    return COMPARISONS[operation](first, second)
