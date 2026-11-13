# Граф зависимостей Python-пакетов, вариант 4

Практическая работа № 2 по конфигурационному управлению.
ИКБО-62-25. Автор: [xyezipster](https://github.com/xyezipster).

Программа читает зависимости из PyPI, строит транзитивный граф
итеративным DFS и выводит его на языке D2. Есть тестовый репозиторий
и поиск обратных зависимостей. Все пять этапов сохранены в своих ветках.


## Пошаговый показ этапа 5

Выполняйте шаги по порядку в обычном терминале macOS. Каждый запуск
программы завершается сам. Нужен Python 3.11 или новее.

### Шаг 1. Открыть папку и выбрать этап

Для локальной папки проекта на этом ноутбуке:

```sh
cd "$HOME/Documents/Конфигурационное управление/konf-upr-practice2-variant4"
git switch stage-5
```

Если проект находится в другом месте, укажите его папку в команде `cd`.

### Шаг 2. Вывести и сохранить описание графа D2

```sh
python3 -B main.py --output output/graph.d2
```

В консоли появится текст со строкой `direction: right`, вершинами и
стрелками. Тот же текст сохранится в `output/graph.d2`.

### Шаг 3. Получить графы трёх настоящих пакетов

Для этих трёх команд нужен интернет:

```sh
python3 -B main.py --config configs/requests.toml --output output/requests.d2
python3 -B main.py --config configs/flask.toml --output output/flask.d2
python3 -B main.py --config configs/rich.toml --output output/rich.d2
```

Каждая команда печатает D2 и сохраняет его в отдельный файл.
Зависимости запрашиваются напрямую из PyPI собственным кодом программы.

### Шаг 4. Открыть готовые примеры визуализации

```sh
open docs/images/requests.svg
open docs/images/flask.svg
open docs/images/rich.svg
```

Это сохранённые в репозитории иллюстрации примеров из `docs/examples/`.
Запуск Python создаёт текст D2 и не перерисовывает эти SVG.
Если нужно отрисовать заново полученные графы из `output/`, команды
для отдельно установленного D2 приведены ниже в справочнике.

### Шаг 5. Показать сравнение с независимым инструментом

```sh
cat docs/comparison.md
```

В отчёте есть таблица для трёх пакетов, условия проверки и объяснение
возможных расхождений. Показать сохранённый вывод pipdeptree:

```sh
cat docs/reference/requests.txt docs/reference/flask.txt docs/reference/rich.txt
```

Это результаты ранее выполненного сравнения, а не новый запрос к PyPI.
pipdeptree использовался отдельно для сравнения; сборщик приложения
не использует его для получения зависимостей.

### Шаг 6. Запустить все автоматические тесты

```sh
python3 -B -m unittest discover -s tests -v
```

Ожидается 37 тестов и строка `OK` в конце.

### Шаг 7. Показать коммиты реализации

```sh
git log --oneline -- src/d2.py tests/test_d2.py docs/comparison.md
```

Реализация уже сохранена и опубликована. Создавать новый коммит для
демонстрации не требуется. Ниже — справочник дополнительных команд.

## Справочник команд и параметров

### Запуск итоговой версии

Нужен Python 3.11+. Устанавливать библиотеки и собирать проект не нужно.
Все команды выполняются из папки репозитория, где находятся `main.py`,
`config.toml`, `src/` и `tests/`.

Программа выполняет один запуск и завершается. Новую проверку запускают
следующей командой в обычном терминале.

Переключиться на полный пятый этап и запустить локальный пример:

```sh
git switch stage-5
python3 -B main.py
```

В `main` результат такой же. Программа напечатает исходник D2,
который начинается со строки `direction: right`.

Прямые и транзитивные зависимости реальных пакетов, нужен интернет:

```sh
python3 -B main.py --config configs/requests.toml
python3 -B main.py --config configs/flask.toml
python3 -B main.py --config configs/rich.toml
python3 -B main.py --help
```

Для запуска в PyCharm достаточно открыть `main.py` и нажать Run.

### Настройки

По умолчанию программа читает `config.toml` рядом с `main.py`:

```toml
package = "A"
repository = "data/demo.json"
test_mode = true
```

| Поле TOML | Назначение |
| --- | --- |
| `package` | Имя анализируемого пакета |
| `repository` | URL PyPI JSON API или путь к тестовому JSON |
| `test_mode` | `true` для локальных данных, `false` для PyPI |

Путь к тестовому JSON считается относительно TOML-файла.
В тестовом режиме пакеты обозначаются большими буквами A–Z.
В реальном режиме имена приводятся к формату PyPI.

| Аргумент запуска | Назначение |
| --- | --- |
| `--config PATH`, `-c PATH` | Выбрать TOML-файл |
| `--reverse [PACKAGE]` | Построить граф обратных зависимостей |
| `--output PATH` | Дополнительно сохранить исходник D2 в файл |
| `--help` | Показать справку |

При `--reverse` без имени целью становится пакет из TOML.
Примеры неверных параметров находятся в `configs/errors/`.
Ошибки конфигурации, сети, JSON и метаданных выводятся без traceback;
программа завершается с кодом 1.

### Получение зависимостей

Программа самостоятельно запрашивает `/pypi/<package>/json` у PyPI
через стандартный `urllib.request` и разбирает `info.requires_dist`.
Готовые средства получения зависимостей и GitHub как источник данных
не используются. Имена, extras и условия окружения обрабатывает свой код.

Для каждой вершины берутся метаданные последней версии. Ограничения
версий сохраняются в требованиях, но программа не устанавливает пакеты
и не подбирает совместимый набор версий, как это делает pip.
Дополнительные группы корневого пакета по умолчанию отключены;
extras, явно указанные во вложенных требованиях, учитываются.
Результат зависит от версии Python и ОС, на которой запущена программа.
Прямые URL-зависимости выводятся как неподдерживаемые с ошибкой.

### Отдельные команды для тестовых графов

Ромб, цикл и изолированная вершина, интернет не требуется:

```sh
python3 -B main.py --config configs/diamond.toml
python3 -B main.py --config configs/cycle.toml
python3 -B main.py --config configs/isolated.toml
```

Цикл сохраняется в диаграмме, программа завершается без зависания.
Для изолированного пакета выводится одна вершина без стрелок.

Обратные зависимости D, цель из TOML и цикл в обратном направлении:

```sh
python3 -B main.py --config configs/demo.toml --reverse D
python3 -B main.py --reverse
python3 -B main.py --config configs/cycle.toml --reverse B
```

Первый пример должен содержать A, B, C, D и E.
В тестовом режиме поиск охватывает весь файл. В реальном режиме
он ограничен графом исходного пакета из TOML:

```sh
python3 -B main.py --config configs/requests.toml --reverse urllib3
```

DFS использует явный стек, без рекурсии. Программа учитывает циклы,
петли, общие зависимости и дополнительные группы из вложенных требований.

### Сохранение и визуализация

Сохранить D2 тестового графа, цикла и обратных зависимостей:

```sh
python3 -B main.py --output output/demo.d2
python3 -B main.py --config configs/cycle.toml --output output/cycle.d2
python3 -B main.py --reverse D --output output/reverse.d2
```

Сохранить три реальных графа, нужен интернет:

```sh
python3 -B main.py --config configs/requests.toml --output output/requests.d2
python3 -B main.py --config configs/flask.toml --output output/flask.d2
python3 -B main.py --config configs/rich.toml --output output/rich.d2
```

Исходник одновременно печатается в консоль и записывается в файл.
Папка `output/` создаётся автоматически и не попадает в Git.

Для отрисовки SVG нужен отдельно установленный [D2](https://d2lang.com/tour/install/):

```sh
d2 output/requests.d2 output/requests.svg
d2 output/flask.d2 output/flask.svg
d2 output/rich.d2 output/rich.svg
```

D2 используется только для отрисовки. Готовые изображения и сравнение
с независимым инструментом находятся в [отчёте](docs/comparison.md).

### Глобальный тест

Команда запускает все автоматические тесты текущего этапа:

```sh
python3 -B -m unittest discover -s tests -v
```

Тесты работают без интернета. Успешный результат заканчивается строкой `OK`.
`FAIL` или `ERROR` означают, что проверка не прошла.

### Отдельные автоматические проверки

Все проверки D2, затем отдельно сохранение файла и обратный граф:

```sh
python3 -B -m unittest discover -s tests -p test_d2.py -v
python3 -B -m unittest discover -s tests -p test_d2.py -k test_cli_writes_and_prints_d2 -v
python3 -B -m unittest discover -s tests -p test_d2.py -k test_cli_reverse_d2 -v
```

Остальные части можно проверить по отдельности:

```sh
python3 -B -m unittest discover -s tests -p test_config.py -v
python3 -B -m unittest discover -s tests -p test_dependencies.py -v
python3 -B -m unittest discover -s tests -p test_graph.py -v
python3 -B -m unittest discover -s tests -p test_reverse.py -v
```

Цепочка из 2001 вершины и обработка циклов:

```sh
python3 -B -m unittest discover -s tests -p test_graph.py -k \
  test_depth_exceeds_recursion_limit -v
python3 -B -m unittest discover -s tests -p test_graph.py -k test_cycle -v
```

### Проверка ошибок

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

Отсутствующая цель обратного поиска:

```sh
python3 -B main.py --reverse Z
```

### Исходники

| Модуль | Основные функции |
| --- | --- |
| `main.py`, `src/cli.py` | `main`, `execute`, `selected_graph`: запуск и выбор режима |
| `src/config.py` | `load_config`, `Config.describe`: настройки |
| `src/repository.py` | `read_json`, `PyPIRepository.dependencies`: PyPI и кэш |
| `src/test_repository.py` | `TestRepository.dependencies`: локальные связи |
| `src/requirements.py` | `parse_requirement`: имя, extras, версии и маркер |
| `src/markers.py`, `src/marker_tokens.py` | `applies`, `tokenize`, `MarkerParser`: условия окружения |
| `src/versions.py` | `version_compare`: сравнение версий в маркерах |
| `src/graph.py` | `build_graph`, `reverse_graph`, `reverse_dependencies`: DFS и обратные связи |
| `src/d2.py` | `format_d2`: описание диаграммы |
| `src/providers.py`, `src/names.py`, `src/tls.py` | Выбор источника, проверка имён и доверенные сертификаты HTTPS |

### Этапы

| Ветка | Содержание |
| --- | --- |
| [stage-1](https://github.com/xyezipster/konf-upr-practice2-variant4/tree/stage-1#readme) | CLI, TOML и проверка настроек |
| [stage-2](https://github.com/xyezipster/konf-upr-practice2-variant4/tree/stage-2#readme) | Прямые зависимости PyPI |
| [stage-3](https://github.com/xyezipster/konf-upr-practice2-variant4/tree/stage-3#readme) | Транзитивный граф, DFS без рекурсии и циклы |
| [stage-4](https://github.com/xyezipster/konf-upr-practice2-variant4/tree/stage-4#readme) | Обратные зависимости |
| [stage-5](https://github.com/xyezipster/konf-upr-practice2-variant4/tree/stage-5#readme) | D2, три визуализации и сравнение |

`main` содержит итоговую версию. Ветки этапов включают предыдущие этапы.

### PyCharm и переключение этапов

В PyCharm откройте папку репозитория, затем `main.py` и нажмите Run.
Без дополнительных параметров используется локальный тестовый пример.

Проверить текущую ветку и вернуться к итоговой версии:

```sh
git branch --show-current
git switch main
```

