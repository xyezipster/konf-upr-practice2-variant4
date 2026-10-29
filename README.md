# Граф зависимостей Python-пакетов, вариант 4

Практическая работа № 2. ИКБО-62-25.
Автор: [xyezipster](https://github.com/xyezipster).

Этап 2 из пяти. Получение прямых зависимостей пакета.

## Быстрый запуск

Нужен Python 3.11+. Устанавливать библиотеки и собирать проект не нужно.
Все команды выполняются из папки репозитория, где находятся `main.py`,
`config.toml`, `src/` и `tests/`.

Программа выполняет один запуск и завершается. Новую проверку запускают
следующей командой в обычном терминале.

```sh
git switch stage-2
python3 -B main.py
```

Для стандартного тестового репозитория будут выведены две прямые
зависимости пакета A:

```text
B
C
```

## Отдельные команды запуска

Прямые зависимости реальных пакетов из PyPI, нужен интернет:

```sh
python3 -B main.py --config configs/requests.toml
python3 -B main.py --config configs/flask.toml
python3 -B main.py --config configs/rich.toml
```

Прямые связи тестового цикла и пакет без зависимостей:

```sh
python3 -B main.py --config configs/cycle.toml
python3 -B main.py --config configs/isolated.toml
python3 -B main.py --help
```

Для цикла команда покажет только B — прямую зависимость A.
Для изолированного A появится сообщение «прямых зависимостей нет».
Транзитивный обход добавляется в третьем этапе.

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

Разбор имени, extras и ограничений версии:

```sh
python3 -B -m unittest discover -s tests -p test_dependencies.py -k RequirementTests -v
```

Условия окружения, версии Python и дополнительные группы:

```sh
python3 -B -m unittest discover -s tests -p test_dependencies.py -k MarkerTests -v
```

Кэш, ответы PyPI, ошибки HTTP и тестовый JSON:

```sh
python3 -B -m unittest discover -s tests -p test_dependencies.py -k RepositoryTests -v
```

Сеть в этих тестах заменяется тестовыми ответами.

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

`PyPIRepository.dependencies` получает метаданные через стандартный
`urllib.request`, `parse_requirement` разбирает Requires-Dist,
`applies` проверяет маркеры окружения. Менеджеры пакетов и готовые
библиотеки получения зависимостей не используются.

## PyCharm и переключение этапов

В PyCharm откройте папку репозитория, затем `main.py` и нажмите Run.
Без дополнительных параметров используется локальный тестовый пример.

Проверить текущую ветку и вернуться к итоговой версии:

```sh
git branch --show-current
git switch main
```

