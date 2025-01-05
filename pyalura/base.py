import requests
from pyalura.utils import sanitize_filename
from lxml import html
import logging
from pyalura.cookie_manager import CookieManager
import unidecode

logger = logging.getLogger(__name__)


class Base:
    def __init__(self) -> None:
        self.cookie_manager = CookieManager()

    @property
    def cookies(self):
        return self.cookie_manager.get_cookies()

    @property
    def headers(self):
        return self.cookie_manager.headers

    def _make_request(self, url, method="GET", **kwargs):
        logger.debug(f"Request: {url}, method: {method}")

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
        slug = unidecode.unidecode(self.title.strip())
        slug_lower = slug.lower().replace(" ", "-")
        return sanitize_filename(slug_lower)
