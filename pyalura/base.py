import requests
from pyalura import utils
from lxml import html
import logging

logger = logging.getLogger(__name__)


class Base:
    def _make_request(self, url, method="GET"):
        logger.debug(f"Request: {url}, method: {method}")

        if method.upper() == "GET":
            method = requests.get
        elif method.upper() == "POST":
            method = requests.post
        elif method.upper() == "HEAD":
            method = requests.head
        else:
            raise NotImplementedError

        response = method(
            url,
            cookies=utils.cookies,
            headers=utils.headers,
        )
        logger.debug(f"Response: {response.status_code}")
        response.raise_for_status()
        return response

    def _fetch_root(self, url):
        response = self._make_request(url)
        return html.fromstring(response.text)
