"""HTTP-загрузка страниц Habr Career с проверкой SSR JSON payload."""

from __future__ import annotations

import time
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup
from bs4 import BeautifulSoup as soup
from requests import exceptions as reqexc


@dataclass
class FetchResult:
    page: BeautifulSoup | None
    status_code: int | None
    error: str | None
    duration_s: float


class PageFetcher:
    _REQUEST_EXCEPTIONS = (
        reqexc.Timeout,
        reqexc.TooManyRedirects,
        reqexc.RequestException,
        reqexc.HTTPError,
    )

    def __init__(self, direct_session: requests.Session) -> None:
        self._direct_session = direct_session

    @staticmethod
    def _page_has_expected_state(page: BeautifulSoup | None, kind: str) -> bool:
        from .template_parser import DumpParser

        return DumpParser.page_has_expected_state(page, kind)

    def fetch_direct(
        self,
        url: str,
        *,
        headers: dict[str, str],
        params: dict | None,
        kind: str,
        timeout: float | tuple[float, float],
    ) -> FetchResult:
        started = time.monotonic()
        status_code: int | None = None
        error: str | None = None
        page: BeautifulSoup | None = None

        try:
            response = self._direct_session.get(
                url, headers=headers, params=params, timeout=timeout
            )
            status_code = response.status_code
            response.raise_for_status()
            page = soup(response.text, "html.parser")
            if page is not None and not self._page_has_expected_state(page, kind):
                error = f"page missing habr {kind} json payload"
                page = None
        except self._REQUEST_EXCEPTIONS as err:
            error = str(err)

        return FetchResult(
            page=page,
            status_code=status_code,
            error=error,
            duration_s=time.monotonic() - started,
        )

    def fetch_via_proxy(
        self,
        url: str,
        *,
        proxy_addr: str,
        headers: dict[str, str],
        params: dict | None,
        kind: str,
        timeout: float | tuple[float, float],
    ) -> FetchResult:
        started = time.monotonic()
        status_code: int | None = None
        error: str | None = None
        page: BeautifulSoup | None = None

        try:
            session = requests.Session()
            session.proxies = {"http": proxy_addr, "https": proxy_addr}
            response = session.get(url, headers=headers, params=params, timeout=timeout)
            status_code = response.status_code
            response.raise_for_status()
            page = soup(response.text, "html.parser")
            if page is not None and not self._page_has_expected_state(page, kind):
                error = f"page missing habr {kind} json payload"
                page = None
        except self._REQUEST_EXCEPTIONS as err:
            error = str(err)

        return FetchResult(
            page=page,
            status_code=status_code,
            error=error,
            duration_s=time.monotonic() - started,
        )
