"""Собственное вычисление маркеров окружения без eval и packaging."""

import operator

from .errors import AppError
from .marker_tokens import VERSION_FIELDS, environment, tokenize
from .versions import COMPARISONS, version_compare


class MarkerParser:
    """Разбирать or, and, скобки и сравнения условий окружения."""

    def __init__(self, expression, values):
        """Подготовить токены и окружение для одного условия."""
        self.tokens = tokenize(expression)
        self.position = 0
        self.values = values

    def accept(self, word):
        """Прочитать служебное слово или скобку при совпадении."""
        if self.position < len(self.tokens):
            if self.tokens[self.position] == ("word", word):
                self.position += 1
                return True
        return False

    def value(self):
        """Прочитать литерал или известную переменную окружения."""
        if self.position == len(self.tokens):
            raise AppError("В условии зависимости не хватает значения")
        kind, value = self.tokens[self.position]
        self.position += 1
        if kind == "literal":
            return value, None
        if value not in self.values:
            raise AppError(f"Неизвестный маркер окружения: {value}")
        return self.values[value], value

    def operation(self):
        """Прочитать сравнение, включая составную операцию not in."""
        if self.accept("not"):
            if not self.accept("in"):
                raise AppError("После not требуется in")
            return "not in"
        if self.position == len(self.tokens):
            raise AppError("В условии нет операции сравнения")
        kind, value = self.tokens[self.position]
        self.position += 1
        if kind != "word":
            raise AppError("Вместо операции сравнения указана строка")
        return value

    def atom(self):
        """Вычислить сравнение либо выражение в скобках."""
        if self.accept("("):
            value = self.or_expression()
            if not self.accept(")"):
                raise AppError("Не закрыта скобка в условии зависимости")
            return value
        left, left_name = self.value()
        operation = self.operation()
        right, right_name = self.value()
        names = {left_name, right_name}
        return compare(left, operation, right, bool(names & VERSION_FIELDS))

    def and_expression(self):
        """Вычислить последовательность сравнений с and."""
        value = self.atom()
        while self.accept("and"):
            right = self.atom()
            value = value and right
        return value

    def or_expression(self):
        """Вычислить последовательность выражений с or."""
        value = self.and_expression()
        while self.accept("or"):
            right = self.and_expression()
            value = value or right
        return value

    def evaluate(self):
        """Проверить полное потребление условия и вернуть результат."""
        result = self.or_expression()
        if self.position != len(self.tokens):
            raise AppError("Лишние символы в условии зависимости")
        return result


def compare(left, operation, right, version=False):
    """Применить операцию сравнения к строкам либо версиям Python."""
    if operation in {"in", "not in"}:
        return (left in right) if operation == "in" else (left not in right)
    if operation == "===":
        return operator.eq(left, right)
    if version or operation == "~=":
        return version_compare(left, operation, right)
    if operation not in COMPARISONS:
        raise AppError(f"Неизвестная операция в условии: {operation}")
    return COMPARISONS[operation](left, right)


def applies(expression, extras=(), values=None):
    """Определить активность зависимости для окружения и выбранных extras."""
    if not expression:
        return True
    base = environment() if values is None else dict(values)
    results = []
    for extra in extras or ("",):
        current = {**base, "extra": extra}
        results.append(MarkerParser(expression, current).evaluate())
    return any(results)
