# AGENTS.md

## Назначение и границы

`docgen` — универсальный Python-инструмент для генерации DOCX и PPTX из строгих JSON-конфигураций. Он не предполагает конкретную организацию, предметную область или тип документа. Состав DOCX задаётся секциями и блоками; PPTX — типизированными слайдами.

Этот корневой файл действует на весь репозиторий. Вложенные `AGENTS.md` не создавайте: контекст намеренно хранится в одном месте.

## Установка и команды

Требуется Python 3.10 или новее.

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
python -m compileall -q docgen
```

Пользовательский CLI:

```bash
docgen init ./project
docgen init ./slides --kind presentation
docgen build ./project/document.json
docgen build ./project/document.json -o ./result.docx
docgen build ./slides/presentation.json -o ./result.pptx
docgen --help
docgen --version
python -m docgen --help
```

Основная точка входа — команда `docgen` либо `python -m docgen`. Не используйте прямой запуск внутренних модулей как пользовательский API.

## Источники истины

При расхождениях используйте такой приоритет:

1. Тесты и фактическая реализация в `docgen/` — поведение runtime.
2. Pydantic-модели в `docgen/config/` — единственный контракт JSON.
3. `README.md` — пользовательская документация и минимальные примеры.

Ручных JSON Schema нет. Не добавляйте параллельный контракт, который придётся синхронизировать с Pydantic.

## Архитектура

Оба формата используют общий поток до выбора генератора:

```text
docgen CLI
  -> load_project(config_path)
  -> выбор модели по kind
  -> Pydantic validation
  -> разрешение content_file и локальных assets
  -> проверка ссылок, цитат и безопасности путей
  -> DocumentGenerator или PresentationGenerator
  -> атомарная запись результата
```

DOCX:

```text
DocumentGenerator
  -> DocumentFormatter
  -> SectionRendererRegistry
  -> BlockRendererRegistry
  -> ResourceRegistry / CitationRegistry / DiagramRegistry
  -> python-docx
```

PPTX:

```text
PresentationGenerator
  -> Theme
  -> typed slide dispatch
  -> SlideFactory
  -> ResourceRegistry / DiagramRegistry
  -> python-pptx
```

Генераторы оркестрируют процесс. Они не должны содержать предметные ветки или логику конкретного вида документа.

## Карта репозитория

```text
docgen/
├── cli.py                 # argparse: init/build
├── io.py                  # атомарное сохранение
├── config/
│   ├── common.py          # строгая базовая модель и enums
│   ├── document.py        # DOCX, секции, блоки, ресурсы
│   ├── presentation.py    # PPTX и discriminated slide unions
│   └── loader.py          # JSON, внешнее содержимое, пути, graph validation
├── document/
│   ├── generator.py       # DOCX orchestration
│   ├── formatter.py       # страницы, стили, номера страниц
│   ├── citations.py       # {{cite:id}} -> [N]
│   ├── resources.py       # lookup по ID
│   ├── sections/          # content, toc, bibliography
│   └── blocks/            # семь block renderers
├── diagrams/              # chart registry и Matplotlib renderers
└── presentation/          # PPTX generator, slides, themes
tests/                     # unit, integration, CLI и smoke tests
```

## Контракты конфигурации

Корневое поле `kind` обязательно:

- `document` выбирает `DocumentConfig` и выход `.docx`;
- `presentation` выбирает `PresentationConfig` и выход `.pptx`.

Для DOCX:

- секции: `content`, `toc`, `bibliography`;
- блоки: `paragraph`, `heading`, `bullet_list`, `numbered_list`, `table`, `figure`, `page_break`;
- `content`-секция содержит ровно одно из `content` или `content_file`;
- внешний content использует тот же массив блоков, что inline content;
- таблицы и рисунки вставляются явно по `ref`, совпадающему с resource ID;
- цитата внутри абзаца или списка имеет форму `{{cite:id}}`;
- библиография содержит только использованные источники в порядке первого упоминания.

Для PPTX slide models являются discriminated union. Не возвращайтесь к одной модели со множеством необязательных полей: тип слайда должен требовать ровно свои данные.

Все модели наследуются от `StrictModel` с `extra="forbid"`. Опечатка в JSON должна приводить к понятной ошибке, а не игнорироваться.

## Маршрутизация изменений

- Новый CLI-сценарий: `docgen/cli.py` и CLI-тест.
- Новое или изменённое JSON-поле: соответствующая Pydantic-модель, loader/consumer, негативный и позитивный тест, README.
- Новый тип секции: модель union в `config/document.py`, renderer в `document/sections/`, импорт регистрации в `sections/__init__.py`, тест.
- Новый тип блока: модель union, renderer в `document/blocks/`, импорт регистрации, unit и generator test.
- Новый тип диаграммы: typed resource model, renderer с `DiagramRegistry.register`, импорт в `diagrams/__init__.py`, PNG test и integration test формата-потребителя.
- Новый тип слайда: отдельная slide model, union, метод `SlideFactory`, typed dispatch в `PresentationGenerator`, тест.
- Форматирование DOCX: `document/formatter.py`; проверяйте значения python-docx и нужный OOXML.
- Общая запись файлов: `docgen/io.py`; не дублируйте atomic-save реализацию.

Сохраняйте небольшие модули с одной ответственностью. Регистрация должна происходить через package `__init__.py`, иначе renderer не будет обнаружен при обычном импорте.

## Тестирование и проверка

Для feature и bugfix используйте RED → GREEN → REFACTOR: сначала тест и ожидаемое падение, затем минимальная реализация.

Минимальная проверка любого изменения:

```bash
python -m pytest -q
python -m compileall -q docgen
git diff --check
```

Дополнительно:

- изменения моделей: позитивные defaults, `extra_forbidden`, cross-field ошибки и refs;
- loader и paths: обычный путь, `..`, симлинк наружу, отсутствующий файл;
- DOCX: открыть результат через `docx.Document` и проверить абзацы, таблицы, shapes или XML;
- PPTX: открыть результат через `pptx.Presentation` и проверить слайды и shapes;
- диаграммы: проверить непустой PNG каждого типа;
- CLI: проверить return code, stdout/stderr и реальный выходной файл.

Перед завершением сделайте smoke-сборку обоих форматов в `mktemp -d`, а не внутри репозитория. Визуальные изменения дополнительно откройте в Word/LibreOffice или PowerPoint/LibreOffice Impress.

## Ошибки и безопасность путей

- Полная валидация выполняется до рендеринга.
- Относительные input paths разрешаются от директории корневого JSON.
- `..` и симлинки не могут вывести input за project root.
- Неизвестный resource ref или citation ID — ошибка, а не молчаливый пропуск.
- Конфигурационный output не может выйти за project root; явный `-o` считается осознанным путём пользователя.
- Выход сначала сохраняется во временный файл рядом с target, затем заменяется через `os.replace`.
- Временные диаграммы создаются в `TemporaryDirectory` и удаляются при успехе и исключении.
- Ошибка не должна повреждать уже существующий target.

CLI пишет краткую диагностическую ошибку в stderr и возвращает 1. Синтаксические ошибки `argparse` возвращают 2.

## Гигиена репозитория

- Не коммитьте `.docx`, `.pptx`, временные диаграммы, caches, virtualenv или `*.egg-info`.
- Не добавляйте реальные пользовательские проекты и документы в корень.
- Не создавайте второй самостоятельный файл агентских инструкций.
- При изменении поведения сначала обновляйте модели и тесты, затем `README.md` и `AGENTS.md`.
- Учитывайте уже существующие изменения в рабочем дереве и не перезаписывайте их без проверки.

## Известные ограничения

- TOC является Word field и может требовать обновления после открытия.
- Прохождение OOXML-тестов не гарантирует визуально корректный макет.
- Нет формул, сносок, HTML/Markdown renderer и внешней plugin-системы.
- Библиографический текст не форматируется по конкретному стандарту.
- Значения по умолчанию нейтральны; специфические требования задаются только конфигурацией.
