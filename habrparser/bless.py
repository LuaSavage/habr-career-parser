from .template_parser import DumpParser


class VacancyBlesser:
    """Дополняет карточки ленты полями со страницы вакансии (например description)."""

    def __init__(self, scrapper) -> None:
        self.scrapper = scrapper

    def __get_blesser(self, vacancy):
        if "url" in vacancy:
            page = self.scrapper.get_vacancy_page(vacancy["url"])
        elif "id" in vacancy:
            page = self.scrapper.get_vacancy_page(id=str(vacancy["id"]))
        else:
            raise ValueError("Vacancy must contain 'url' or 'id' to bless fields")
        return DumpParser.parse_vacancy_page(page)

    def bless_fields(self, vacancy, fields):
        if isinstance(vacancy, list):
            for vac in vacancy:
                self.bless_fields(vac, fields)
            return vacancy

        vacancy_full_data = self.__get_blesser(vacancy)
        for key in fields:
            if key in vacancy_full_data:
                vacancy[key] = vacancy_full_data[key]
            if key == "description":
                if "description_html" in vacancy_full_data:
                    vacancy["description_html"] = vacancy_full_data["description_html"]
                if "description_text" in vacancy_full_data:
                    vacancy["description_text"] = vacancy_full_data["description_text"]
        return vacancy
