# Граф зависимостей Python-пакетов, вариант 4

Практическая работа № 2. ИКБО-62-25.
Автор: [xyezipster](https://github.com/xyezipster).

Этап 1 из пяти. Проверка TOML-настроек и вывод параметров.

## Быстрый запуск

Нужен Python 3.11+. Устанавливать библиотеки и собирать проект не нужно.
Все команды выполняются из папки репозитория, где находятся `main.py`,
`config.toml`, `src/` и `tests/`.

Программа выполняет один запуск и завершается. Новую проверку запускают
следующей командой в обычном терминале.

```sh
git switch stage-1
python3 -B main.py
```

Программа выводит три строки `package=...`, `repository=...`,
`test_mode=...`. На этом этапе данные пакета ещё не запрашиваются.

## Отдельные команды запуска

Другой локальный конфиг и настройки реального репозитория:

```sh
python3 -B main.py --config configs/demo.toml
python3 -B main.py --config configs/requests.toml
python3 -B main.py --help
```

Вторая команда тоже только показывает настройки, сеть на первом этапе
не используется.

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

Проверка всех настроек и способов запуска:

```sh
python3 -B -m unittest discover -s tests -p test_config.py -v
```

Только неверные значения параметров:

```sh
python3 -B -m unittest discover -s tests -p test_config.py -k test_invalid_parameters -v
```

Только запуск из другой папки:

```sh
python3 -B -m unittest discover -s tests -p test_config.py -k \
  test_direct_launch_from_another_directory -v
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

`src/config.py`: `load_config` читает TOML, `Config.describe` печатает
настройки. `src/cli.py`: `main` и `execute` управляют запуском.

## PyCharm и переключение этапов

В PyCharm откройте папку репозитория, затем `main.py` и нажмите Run.
Без дополнительных параметров используется локальный тестовый пример.

Проверить текущую ветку и вернуться к итоговой версии:

```sh
git branch --show-current
git switch main
```

