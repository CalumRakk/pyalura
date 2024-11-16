from datetime import datetime
from pyalura.utils import ArticleType
from pyalura import utils
from .base import Base
from lxml import html
from requests_cache import CachedResponse

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyalura.section import Section


class Item(Base):
    def __init__(
        self, url: str, title: str, index: str, type: ArticleType, section: "Section"
    ):
        self.url = url
        self.title = title
        self.index = index
        self.type = type
        self.section = section

    def get_content(self):
        response = self._make_request(self.url)
        root = html.fromstring(response.text)

        item_video = None
        item_content = None
        item_raw_html = response.text
        if self.type == utils.ArticleType.VIDEO:
            item_video = utils.fetch_item_video(self.url)
            item_content = utils.get_item_content(root)
        else:
            item_content = utils.get_item_content(root)

        return {
            "video": item_video,
            "content": item_content,
            "raw_html": item_raw_html,
            "section": self.section,
            "is_cache": isinstance(response, CachedResponse),
        }
