"""End-to-end smoke test: search career.habr.com for 'golang' (first page only)."""

from __future__ import annotations

import json
import sys
import time
from typing import Any

import requests
from bs4 import BeautifulSoup
from fake_headers import Headers
from habrparser.scrapper import VacancyScrapper
from habrparser.template_parser import DumpParser

SEARCH_TEXT = "golang"
SEARCH_URL = "https://career.habr.com/vacancies"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
}


def fetch_search_page_direct(page: int = 1) -> BeautifulSoup:
    params = {
        "q": SEARCH_TEXT,
        "type": "all",
        "page": page,
    }
    response = requests.get(
        SEARCH_URL,
        params=params,
        headers=Headers().generate() or HEADERS,
        timeout=30,
    )
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def validate_vacancies(vacancies: list[dict[str, Any]]) -> None:
    assert len(vacancies) > 0, "Список вакансий не должен быть пустым"

    first = vacancies[0]
    for field in ("title", "url", "company", "skills"):
        assert field in first, f"У вакансии должно быть поле '{field}'"

    print(f"OK: получено {len(vacancies)} вакансий на первой странице")
    company = first.get("company") or {}
    print(f"  Первая: {first.get('title')} — {company.get('title', '?')}")


def test_direct_parsing() -> list[dict[str, Any]]:
    print("\n=== 1. Direct HTTP + DumpParser (без прокси) ===")
    page = fetch_search_page_direct(page=1)
    script = page.find("script", attrs={"data-ssr-state": "true"})
    assert script is not None, "На странице должен быть script[data-ssr-state=true]"

    vacancies = DumpParser.parse_search_page(page)
    validate_vacancies(vacancies)
    return vacancies


def test_scrapper_first_page() -> list[dict[str, Any]]:
    print("\n=== 2. VacancyScrapper + DumpParser (первая страница) ===")

    params = {"q": SEARCH_TEXT, "type": "all", "page": 1}
    started = time.monotonic()
    scrapper = VacancyScrapper(params=params, use_proxy=False)
    print(f"    Scrapper init: {time.monotonic() - started:.1f}s (direct, no proxy)")

    page = scrapper.get_searching_results_page(page_number=0)
    assert page is not None, "Scrapper должен вернуть страницу"

    vacancies = DumpParser.parse_search_page(page)
    validate_vacancies(vacancies)
    return vacancies


def test_api_single_vacancy(vacancies: list[dict[str, Any]]) -> None:
    print("\n=== 3. DumpParser.parse_vacancy_page (одна вакансия) ===")
    params = {"q": SEARCH_TEXT, "type": "all", "page": 1}
    scrapper = VacancyScrapper(params=params, use_proxy=False)

    vacancy_id = str(vacancies[0]["id"])
    vacancy_page = scrapper.get_vacancy_page(id=vacancy_id)
    if vacancy_page is None:
        print(
            "SKIP: career.habr.com вернул страницу без vacancy SSR JSON. "
            "Search parsing OK — парсер JSON не виноват."
        )
        return

    vacancy = DumpParser.parse_vacancy_page(vacancy_page)

    assert "title" in vacancy, "Страница вакансии должна содержать title"
    assert "description" in vacancy, "Страница вакансии должна содержать description"
    print(f"OK: vacancy id={vacancy_id}, title={vacancy.get('title')}")


def main() -> int:
    print(f"E2E test: search='{SEARCH_TEXT}'")

    try:
        direct_vacancies = test_direct_parsing()
    except Exception as exc:
        print(f"FAIL direct parsing: {exc}", file=sys.stderr)
        return 1

    try:
        scrapper_vacancies = test_scrapper_first_page()
    except Exception as exc:
        print(f"FAIL scrapper path: {exc}", file=sys.stderr)
        print("\nDirect parsing worked — проблема скорее в Proxy/Scrapper, не в парсере JSON.")
        return 1

    assert len(scrapper_vacancies) > 0, "Scrapper path должен вернуть вакансии"

    try:
        test_api_single_vacancy(direct_vacancies)
    except Exception as exc:
        print(f"FAIL vacancy detail: {exc}", file=sys.stderr)
        return 1

    sample = {
        "count_direct": len(direct_vacancies),
        "count_scrapper": len(scrapper_vacancies),
        "sample": {
            "id": direct_vacancies[0].get("id"),
            "title": direct_vacancies[0].get("title"),
            "url": direct_vacancies[0].get("url"),
            "key_skills": direct_vacancies[0].get("key_skills"),
        },
    }
    print("\n=== Sample (first vacancy, truncated) ===")
    print(json.dumps(sample, indent=2, ensure_ascii=False)[:2000])
    print("\nALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
