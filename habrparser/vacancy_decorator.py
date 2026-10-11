from __future__ import annotations

import codecs
import re
import unicodedata
from typing import Any

import html2text

from .scrapper import VacancyScrapper


class Decorator:
    @staticmethod
    def sanitize_string(raw_string: str) -> str:
        raw_string = codecs.encode(str(raw_string), "utf8")
        raw_string = codecs.decode(raw_string, "utf8")
        raw_string = unicodedata.normalize("NFKD", raw_string).rstrip()
        return re.sub(r"\n", "", raw_string)

    def decorate_url(self, vacancy: dict[str, Any]) -> None:
        href = vacancy.get("href")
        if isinstance(href, str) and href.startswith("http"):
            vacancy["url"] = href
            return
        if isinstance(href, str) and href.startswith("/"):
            vacancy["url"] = "https://career.habr.com" + href
            return
        vacancy_id = vacancy.get("id")
        if vacancy_id is not None:
            vacancy["url"] = f"{VacancyScrapper.get_vacancy_url()}/{vacancy_id}"

    def decorate_key_skills(self, vacancy: dict[str, Any]) -> None:
        skills = vacancy.get("skills") or []
        titles: list[str] = []
        for skill in skills:
            if isinstance(skill, dict) and skill.get("title"):
                titles.append(str(skill["title"]))
            elif isinstance(skill, str):
                titles.append(skill)
        vacancy["key_skills"] = titles


class InterfaceVacancyDecorator:
    def __init__(self, vacancy_data):
        self.vacancy_data = []
        if isinstance(vacancy_data, list):
            for vacancy in vacancy_data:
                self.vacancy_data.append(self.decorate(vacancy))
        elif isinstance(vacancy_data, dict):
            self.vacancy_data = self.decorate(vacancy_data)

    def decorate(self, vacancy):
        pass


class SearchedVacancyDecorator(Decorator, InterfaceVacancyDecorator):
    def decorate(self, vacancy):
        self.decorate_url(vacancy)
        self.decorate_key_skills(vacancy)
        return vacancy


class ViewVacancyDecorator(SearchedVacancyDecorator):
    html2text = html2text.HTML2Text()

    def decorate_description(self, vacancy: dict[str, Any]) -> None:
        description = vacancy.get("description")
        if not isinstance(description, str) or not description:
            return
        vacancy["description_html"] = description
        self.html2text.ignore_links = True
        vacancy["description_text"] = self.sanitize_string(self.html2text.handle(description))

    def decorate(self, vacancy):
        super().decorate(vacancy)
        self.decorate_description(vacancy)
        return vacancy
