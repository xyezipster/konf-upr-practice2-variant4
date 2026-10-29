# Граф зависимостей Python-пакетов, вариант 4

Практическая работа № 2. ИКБО-62-25.
Автор: [xyezipster](https://github.com/xyezipster).

Этап 4 из пяти. Поиск обратных зависимостей.

## Быстрый запуск

Нужен Python 3.11+. Устанавливать библиотеки и собирать проект не нужно.
Все команды выполняются из папки репозитория, где находятся `main.py`,
`config.toml`, `src/` и `tests/`.

Программа выполняет один запуск и завершается. Новую проверку запускают
следующей командой в обычном терминале.

```sh
git switch stage-4
python3 -B main.py
```

Обычный запуск показывает прямой транзитивный граф.
Флаг `--reverse` включает поиск пакетов, которые зависят от выбранной цели.

## Отдельные команды запуска

Все прямые и транзитивные предки D в тестовом репозитории:

```sh
python3 -B main.py --config configs/demo.toml --reverse D
```

Ожидаемый результат:

```text
A: (нет)
B: A
C: A, E
D: B, C
E: (нет)
```

E тоже найден: в тестовом режиме проверяется весь файл,
включая пакеты, недостижимые из A по прямым рёбрам.

Цель из TOML, цикл и изолированная вершина:

```sh
python3 -B main.py --reverse
python3 -B main.py --config configs/cycle.toml --reverse B
python3 -B main.py --config configs/isolated.toml --reverse A
```

Первый пример покажет `A: (нет)`, цикл завершится без зависания.

Обратные зависимости urllib3 внутри графа requests, нужен интернет:

```sh
python3 -B main.py --config configs/requests.toml --reverse urllib3
```

В реальном режиме поиск ограничен графом исходного пакета из TOML.
Весь реестр PyPI не сканируется.

Отсутствующая цель — ожидаемая ошибка:

```sh
python3 -B main.py --reverse Z
```

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

Все проверки обратных зависимостей:

```sh
python3 -B -m unittest discover -s tests -p test_reverse.py -v
```

Только поиск всех предков в тестовом файле:

```sh
python3 -B -m unittest discover -s tests -p test_reverse.py -k \
  test_all_ancestors_in_test_repository -v
```

Только цикл и отсутствующая цель, каждая команда отдельно:

```sh
python3 -B -m unittest discover -s tests -p test_reverse.py -k test_reverse_cycle -v
python3 -B -m unittest discover -s tests -p test_reverse.py -k test_unknown_target -v
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

`reverse_graph` разворачивает рёбра, `reverse_dependencies` использует
тот же `build_graph` из третьего этапа для обхода обратных связей.

## PyCharm и переключение этапов

В PyCharm откройте папку репозитория, затем `main.py` и нажмите Run.
Без дополнительных параметров используется локальный тестовый пример.

Проверить текущую ветку и вернуться к итоговой версии:

```sh
git branch --show-current
git switch main
```

