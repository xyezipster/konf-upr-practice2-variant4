"""Лексический разбор условий окружения из Requires-Dist."""

import platform
import re
import sys
import os

from .errors import AppError

TOKEN = re.compile(r"\s*(?:('[^']*'|\"[^\"]*\")|"
                   r"(===|~=|==|!=|<=|>=|<|>|\(|\)|[A-Za-z_]+))")
VERSION_FIELDS = {"python_version", "python_full_version",
                  "implementation_version"}


def environment():
    """Собрать значения стандартных маркеров для текущего Python и ОС."""
    return {
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
        "python_full_version": platform.python_version(),
        "implementation_version": platform.python_version(),
        "implementation_name": sys.implementation.name,
        "os_name": os.name,
        "sys_platform": sys.platform,
        "platform_machine": platform.machine(),
        "platform_release": platform.release(),
        "platform_system": platform.system(),
        "platform_version": platform.version(),
        "platform_python_implementation": platform.python_implementation(),
        "extra": "",
    }


def tokenize(expression):
    """Выделить строки, имена переменных, операции и скобки."""
    expression = expression.strip()
    tokens, position = [], 0
    while position < len(expression):
        match = TOKEN.match(expression, position)
        if match is None:
            raise AppError(f"Неверное условие зависимости: {expression}")
        literal, word = match.groups()
        token = ("literal", literal[1:-1]) if literal else ("word", word)
        tokens.append(token)
        position = match.end()
    return tokens
