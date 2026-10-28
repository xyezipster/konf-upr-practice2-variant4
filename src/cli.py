"""Аргументы командной строки и запуск текущего этапа."""

import argparse
from pathlib import Path
import sys

from .config import load_config
from .errors import AppError
from .providers import repository
from .graph import build_graph, reverse_dependencies
from .d2 import format_d2
from .names import normalize, test_name

DEFAULT_CONFIG = Path(__file__).resolve().parents[1] / "config.toml"


def arguments(argv=None):
    """Получить путь к TOML-конфигурации из командной строки."""
    parser = argparse.ArgumentParser(description="Граф зависимостей, вариант 4")
    parser.add_argument("-c", "--config", type=Path, default=DEFAULT_CONFIG,
                        help="путь к TOML-файлу")
    parser.add_argument("--reverse", nargs="?", const="",
                        metavar="PACKAGE", help="обратные зависимости")
    parser.add_argument("--output", type=Path,
                        help="дополнительно сохранить исходник D2 в файл")
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
    """Пятый этап: вывести выбранный граф на языке D2."""
    return format_d2(selected_graph(config, options))


def main(argv=None):
    """Прочитать конфигурацию и сообщить об ошибках без traceback."""
    options = arguments(argv)
    try:
        config = load_config(options.config)
        result = execute(config, options)
        if options.output:
            options.output.parent.mkdir(parents=True, exist_ok=True)
            options.output.write_text(result, encoding="utf-8")
        print(result, end="")
    except (AppError, OSError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 1
    return 0
