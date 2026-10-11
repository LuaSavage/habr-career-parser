import json

from .vacancy_decorator import SearchedVacancyDecorator, ViewVacancyDecorator


class DumpParser:
    @classmethod
    def __extract_raw_json(cls, page) -> str:
        script = page.find("script", attrs={"data-ssr-state": "true"})
        if script is None:
            raise ValueError("Page state JSON not found (missing data-ssr-state script)")
        raw = script.string or script.get_text()
        text = (raw or "").strip()
        if not text.startswith("{"):
            raise ValueError("Page state JSON not found (empty or non-JSON script)")
        return text

    @classmethod
    def __parse_template(cls, page):
        raw_json = cls.__extract_raw_json(page)
        return json.loads(raw_json)

    @classmethod
    def page_has_expected_state(cls, page, kind: str) -> bool:
        if page is None:
            return False
        try:
            json_obj = cls.__parse_template(page)
        except (ValueError, json.JSONDecodeError, TypeError):
            return False

        if kind == "search":
            vacancies = json_obj.get("vacancies")
            return isinstance(vacancies, dict) and isinstance(vacancies.get("list"), list)
        if kind == "vacancy":
            vacancy = json_obj.get("vacancy")
            return isinstance(vacancy, dict) and "id" in vacancy
        return False

    @classmethod
    def get_search_page_count(cls, searching_page) -> int:
        json_obj = cls.__parse_template(searching_page)
        meta = json_obj["vacancies"]["meta"]
        total_pages = meta.get("totalPages")
        if isinstance(total_pages, int) and total_pages > 0:
            return total_pages
        return 1

    @classmethod
    def parse_search_page(cls, searching_page):
        json_obj = cls.__parse_template(searching_page)
        vacancies = json_obj["vacancies"]["list"]
        SearchedVacancyDecorator(vacancies)
        return vacancies

    @classmethod
    def parse_vacancy_page(cls, page):
        json_obj = cls.__parse_template(page)
        if "vacancy" not in json_obj:
            raise ValueError("vacancy not found in page state (blocked or incomplete page)")
        vacancy = json_obj["vacancy"]
        if json_obj.get("company") is not None:
            vacancy["company_sidebar"] = json_obj["company"]
        if json_obj.get("similar") is not None:
            vacancy["similar"] = json_obj["similar"]
        ViewVacancyDecorator(vacancy)
        return vacancy
