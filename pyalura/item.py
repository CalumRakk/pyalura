from datetime import datetime, timedelta
from pyalura.utils import ArticleType
from pyalura import utils
from .base import Base
from lxml import html
from requests_cache import CachedResponse
import random

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

    def get_content(self) -> dict:
        """
        Devuelve el contenido del episodio/tarea del curso.

        dict: Un diccionario con información sobre el contenido del episodio/tarea, que incluye:
            - "video": Datos del video (si es un video).
            - "content": Contenido del artículo.
            - "raw_html": HTML sin procesar del artículo.

        Nota: tiene implementado internamente una espera si ha solicitado el contenido de un episodio/tarea muy recientemente.
        """

        response = self._make_request(self.url)
        root = html.fromstring(response.text)

        is_cache = isinstance(response, CachedResponse)
        if not is_cache:
            if self.section.course.last_item_get_content_time is None:
                self.section.course.last_item_get_content_time = datetime.now()
            else:
                diff_time = (
                    datetime.now() - self.section.course.last_item_get_content_time
                )
                if diff_time.total_seconds() < 15:
                    randint = random.randint(5, 30)
                    utils.sleep_program(randint)
                    self.section.course.last_item_get_content_time = datetime.now()

        item_video = None
        item_content = None
        item_raw_html = response.text
        if self.type == utils.ArticleType.VIDEO:
            item_video = utils.fetch_item_video(self.url)
            item_content = utils.get_item_content(root)
        else:
            item_content = utils.get_item_content(root)

        return {"video": item_video, "content": item_content, "raw_html": item_raw_html}
