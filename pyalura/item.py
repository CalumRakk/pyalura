from datetime import datetime, timedelta
from pyalura.utils import ArticleType
from pyalura import utils
import html2text
from .base import Base
from lxml import html
from urllib.parse import urlparse, parse_qs, urljoin
from requests_cache import CachedResponse
import requests_cache
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
        super().__init__()

    def get_content(self) -> dict:
        """
        Devuelve el contenido del episodio/tarea del curso.
        """
        response = self._make_request(self.url)
        root = html.fromstring(response.text)

        if not isinstance(response, CachedResponse):
            self._should_wait_for_request()

        item_content = self._get_content(root)
        item_raw_html = response.text
        videos = None

        if self.type == utils.ArticleType.VIDEO:
            videos = self._fetch_item_video()

        return {"videos": videos, "content": item_content, "raw_html": item_raw_html}

    def _should_wait_for_request(self) -> bool:
        """
        Determina si es necesario esperar antes de hacer la siguiente solicitud.
        """
        if self.section.course.last_item_get_content_time is None:
            self.section.course.last_item_get_content_time = datetime.now()
            return False

        diff_time = datetime.now() - self.section.course.last_item_get_content_time
        if diff_time.total_seconds() < 15:
            randint = random.randint(5, 30)
            utils.sleep_program(randint)
            self.section.course.last_item_get_content_time = datetime.now()
            return True
        return False

    def _is_video_expired(self, video_url: str) -> bool:
        """
        Verifica si el video ha expirado en el caché.
        """
        url_parsed = urlparse(video_url)
        query_params = {
            key: value[0] for key, value in parse_qs(url_parsed.query).items()
        }
        expires = int(query_params["X-Amz-Expires"])
        request_time = datetime.strptime(query_params["X-Amz-Date"], "%Y%m%dT%H%M%SZ")
        return datetime.utcnow() - request_time >= timedelta(seconds=expires)

    def _fetch_item_video(self) -> dict:
        """
        Obtiene los videos del artículo.
        """
        url_api = f"{urljoin('https://app.aluracursos.com/', self.url)}/video"
        response = self._make_request(url_api)
        videos = response.json()
        videos = {i["quality"]: i for i in videos}

        if isinstance(response, CachedResponse) and self._is_video_expired(
            videos["hd"]["mp4"]
        ):
            cache = requests_cache.get_cache()
            cache.delete(response.cache_key)
            return self._fetch_item_video()

        return videos

    def _get_content(self, root) -> str:
        """
        Extrae y convierte el contenido HTML de un episodio/tarea en formato Markdown.
        """
        element = root.find(".//section[@id='task-content']")
        if element is None:
            raise ValueError("No se encontró el contenido de la tarea.")
        header = root.find(".//span[@class='task-body-header-title-text']").text.strip()
        content = html.tostring(element)
        return self._convert_html_to_markdown(content, header)

    def _convert_html_to_markdown(self, html_content: bytes, header: str) -> str:
        """
        Convierte el contenido HTML a formato Markdown.
        """
        string = html2text.html2text(html_content.decode("UTF-8"))
        return f"# {header}\n\n{string}"
