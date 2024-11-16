import requests
from . import utils
from lxml import html


class Base:
    def _make_request(self, url, method="GET"):
        response = requests.request(
            method,
            url,
            cookies=utils.cookies,
            headers=utils.headers,
        )

        response.raise_for_status()
        return response

    def _fetch_root(self, url):
        response = self._make_request(url)
        return html.fromstring(response.text)
