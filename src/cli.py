"""Аргументы командной строки и запуск текущего этапа."""

import argparse
from pathlib import Path
import sys

from .config import load_config
from .errors import AppError
from .providers import repository
from .graph import build_graph, format_graph, reverse_dependencies
from .names import normalize, test_name

DEFAULT_CONFIG = Path(__file__).resolve().parents[1] / "config.toml"


def arguments(argv=None):
    """Получить путь к TOML-конфигурации из командной строки."""
    parser = argparse.ArgumentParser(description="Граф зависимостей, вариант 4")
    parser.add_argument("-c", "--config", type=Path, default=DEFAULT_CONFIG,
                        help="путь к TOML-файлу")
    parser.add_argument("--reverse", nargs="?", const="",
                        metavar="PACKAGE", help="обратные зависимости")
    return parser.parse_args(argv)


def selected_graph(config, options):
    """Получить прямой либо обратный граф для выбранного режима."""
    source = repository(config)
    if options.reverse is not None:
        target = options.reverse or config.package
        target = test_name(target) if config.test_mode else normalize(target)
        return reverse_dependencies(config.package, target, source)
    return build_graph(config.package, source)


def execute(config, options):
    """Четвёртый этап: показать прямой либо обратный граф."""
    return format_graph(selected_graph(config, options))


def main(argv=None):
    """Прочитать конфигурацию и сообщить об ошибках без traceback."""
    options = arguments(argv)
    try:
        config = load_config(options.config)
        print(execute(config, options))
    except (AppError, OSError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    return 0
