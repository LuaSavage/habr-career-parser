import json
import logging

from habrparser import Api, VacancyScrapper, configure_logging

configure_logging(logging.INFO)

params = {
    "q": "golang junior",
    "type": "all",
    "page": 1,
}

scrapper = VacancyScrapper(params=params, use_proxy="adaptive")
habr_api = Api(scrapper)

vac = habr_api.get_vacancies(bless_fields=["description"])

logging.getLogger(__name__).info("Total vacancies: %s", len(vac))
print(json.dumps(vac, indent=4, ensure_ascii=False))
