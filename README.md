# Habr Career Parser

Библиотека для выгрузки вакансий [Хабр Карьеры](https://career.habr.com/vacancies?type=all).
Источник данных — SSR JSON в HTML (`script[data-ssr-state=true]`), а не разбор DOM-карточек.

Архитектура повторяет [`hh_ru_parser`](../hh_ru_parser): **Api**, **VacancyScrapper**, **DumpParser**, **VacancyBlesser**, proxy race (`always` / `never` / `adaptive`).

На ленте уже есть навыки, зарплата, компания, грейд. Полный HTML-текст вакансии есть только на detail-странице — его подтягивает `bless_fields=["description"]`.

## Установка

```bash
cd habr-career-parser
python3 -m venv .venv   # если нет ensurepip: pip install virtualenv && python -m virtualenv .venv
source .venv/bin/activate
pip install -e .
```

## Пример

```python
from habrparser import Api, VacancyScrapper, configure_logging
import logging

configure_logging(logging.INFO)

scrapper = VacancyScrapper(
    params={"q": "golang", "type": "all", "page": 1},
    use_proxy="adaptive",
)
api = Api(scrapper)
vacancies = api.get_vacancies(bless_fields=["description"])
```

Карточка ленты использует нативные поля Habr: `title`, `company`, `skills`, `salary`.
Дополнительно декоратор кладёт `url` и `key_skills` (список строк).

## Дамп

```bash
python examples/full_dump.py --query golang --max-pages 1 --max-vacancies 3 --use-proxy never
```

## E2E

```bash
python tests/e2e_test.py
```

Живой запрос к `career.habr.com`.

## Пагинация

Habr нумерует страницы с **1**. `VacancyScrapper.get_searching_results_page(page_number)` принимает 0-based индекс (как hhparser) и шлёт `page=page_number+1`.
