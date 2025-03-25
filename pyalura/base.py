import requests
from lxml import html
import logging
from pyalura.cookie_manager import CookieManager
from pyalura.utils import string_to_slug


logger = logging.getLogger(__name__)


class Base:
    def __init__(self, cookies_path=None) -> None:
        self.cookie_manager = CookieManager(cookies_path=cookies_path)

    @property
    def cookies(self):
        # TODO: mejorar la logica de la carga de cookies, no deberia guarde en la instancia de esta Clase.
        if not hasattr(self, "_cookies"):
            cookies = self.cookie_manager.get_cookies()
            setattr(self, "_cookies", cookies)
        return getattr(self, "_cookies")

    @property
    def headers(self):
        return self.cookie_manager.headers

    def _make_request(self, url, method="GET", **kwargs):
        logger.debug(f"Request: {url}, method: {method}, kwargs: {kwargs}")

        if method.upper() == "GET":
            method = requests.get
        elif method.upper() == "POST":
            method = requests.post
        elif method.upper() == "HEAD":
            method = requests.head
        else:
            raise NotImplementedError

        response = method(url, cookies=self.cookies, headers=self.headers, **kwargs)
        logger.debug(f"Response: {response.status_code}")
        response.raise_for_status()
        return response

    def _fetch_root(self, url):
        response = self._make_request(url)
        return html.fromstring(response.text)

    @property
    def title_slug(self):
        return string_to_slug(self.title)
