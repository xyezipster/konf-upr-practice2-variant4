"""Аргументы командной строки и запуск текущего этапа."""

import argparse
from pathlib import Path
import sys

from .config import load_config
from .errors import AppError
from .providers import repository
from .graph import build_graph, format_graph

DEFAULT_CONFIG = Path(__file__).resolve().parents[1] / "config.toml"


def arguments(argv=None):
    """Получить путь к TOML-конфигурации из командной строки."""
    parser = argparse.ArgumentParser(description="Граф зависимостей, вариант 4")
    parser.add_argument("-c", "--config", type=Path, default=DEFAULT_CONFIG,
                        help="путь к TOML-файлу")
    return parser.parse_args(argv)


def execute(config, options):
    """Третий этап: построить и показать транзитивный граф зависимостей."""
    source = repository(config)
    return format_graph(build_graph(config.package, source))


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
