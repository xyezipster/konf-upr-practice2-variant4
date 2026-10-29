# Граф зависимостей Python-пакетов, вариант 4

Практическая работа № 2. ИКБО-62-25.
Автор: [xyezipster](https://github.com/xyezipster).

Этап 3 из пяти. Полный граф зависимостей, DFS без рекурсии.

## Быстрый запуск

Нужен Python 3.11+. Устанавливать библиотеки и собирать проект не нужно.
Все команды выполняются из папки репозитория, где находятся `main.py`,
`config.toml`, `src/` и `tests/`.

Программа выполняет один запуск и завершается. Новую проверку запускают
следующей командой в обычном терминале.

```sh
git switch stage-3
python3 -B main.py
```

Ожидаемый граф стандартного примера:

```text
A: B, C
B: D
C: D
D: (нет)
```

Общая зависимость D выводится одной вершиной.

## Отдельные команды запуска

Ромб, цикл и изолированная вершина без сетевых запросов:

```sh
python3 -B main.py --config configs/diamond.toml
python3 -B main.py --config configs/cycle.toml
python3 -B main.py --config configs/isolated.toml
```

Для цикла появятся A: B, B: C, C: A, после чего программа завершится.
Для изолированной вершины выводится `A: (нет)`.

Полный граф реального пакета из PyPI, нужен интернет:

```sh
python3 -B main.py --config configs/requests.toml
python3 -B main.py --help
```

Обход выполняется DFS с явным стеком, без рекурсии.
Ограничения версий сохраняются в требованиях; для каждой вершины берутся
метаданные последней версии, совместимый набор для установки не подбирается.

## Настройки

```toml
package = "A"
repository = "data/demo.json"
test_mode = true
```

| Поле | Что задаёт |
| --- | --- |
| `package` | Имя пакета, для тестовых данных большие буквы A–Z |
| `repository` | URL репозитория PyPI или путь к тестовому JSON |
| `test_mode` | `true` для локального файла, `false` для PyPI |

Относительный путь к JSON считается от TOML-файла.
`--config PATH` или `-c PATH` выбирает настройки, `--help` показывает справку.

## Глобальный тест

Команда запускает все автоматические тесты текущего этапа:

```sh
python3 -B -m unittest discover -s tests -v
```

Тесты работают без интернета. Успешный результат заканчивается строкой `OK`.
`FAIL` или `ERROR` означают, что проверка не прошла.

## Отдельные автоматические проверки

Все проверки графа:

```sh
python3 -B -m unittest discover -s tests -p test_graph.py -v
```

Только цикл:

```sh
python3 -B -m unittest discover -s tests -p test_graph.py -k test_cycle -v
```

Только цепочка из 2001 вершины, превышающая обычный предел рекурсии:

```sh
python3 -B -m unittest discover -s tests -p test_graph.py -k \
  test_depth_exceeds_recursion_limit -v
```

Только ромб и порядок DFS:

```sh
python3 -B -m unittest discover -s tests -p test_graph.py -k test_diamond_and_dfs_order -v
```

## Проверка ошибок

Каждую команду можно выполнить отдельно:

```sh
python3 -B main.py --config configs/errors/bad-package.toml
python3 -B main.py --config configs/errors/bad-repository.toml
python3 -B main.py --config configs/errors/bad-mode.toml
python3 -B main.py --config configs/errors/missing-file.toml
python3 -B main.py --config configs/missing.toml
```

Ожидаются сообщения `Ошибка:` о пустом имени, неверном URL,
неверном типе `test_mode`, отсутствующем JSON и отсутствующем TOML.
Эти примеры специально завершаются с кодом 1 и проверяют обработку ошибок.

## Основные функции

`build_graph` и `format_graph` находятся в `src/graph.py`.
Получение метаданных, разбор Requires-Dist и маркеры окружения
работают так же, как на втором этапе.

## PyCharm и переключение этапов

В PyCharm откройте папку репозитория, затем `main.py` и нажмите Run.
Без дополнительных параметров используется локальный тестовый пример.

Проверить текущую ветку и вернуться к итоговой версии:

```sh
git branch --show-current
git switch main
```

