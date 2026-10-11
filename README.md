# Habr Career Parser

Рашение для парсинга вакансий с Хабр Карьеры.
Репозиторий написан в учебных целях анализа рынка труда и выполнения лабораторных работ.

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

## Еще пример

```bash
python examples/full_dump.py --query golang --max-pages 1 --max-vacancies 3 --use-proxy never
```

## E2E

```bash
python tests/e2e_test.py
```

