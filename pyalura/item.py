from datetime import datetime, timedelta
from pyalura.utils import ArticleType
from pyalura import utils
from pathlib import Path
import html2text
from .base import Base
from lxml import html
from urllib.parse import urlparse, parse_qs, urljoin
import random
from typing import TYPE_CHECKING
from pyalura.item_utils import get_answers
from pyalura.choice import Answer, Choice

if TYPE_CHECKING:
    from pyalura.section import Section


class Item(Base):
    def __init__(
        self,
        url: str,
        title: str,
        index: str,
        type: ArticleType,
        section: "Section",
        is_marked_as_seen: bool,
    ):
        self.url = url
        self.title = title
        self.index = index
        self.type = type
        self.section = section
        self.is_marked_as_seen = is_marked_as_seen
        super().__init__()

    def get_content(self) -> dict:
        """
        Devuelve el contenido del episodio/tarea del curso.
        """
        if self._should_wait_for_request():
            self._wait_for_request()

        response = self._make_request(self.url)
        root = html.fromstring(response.text)

        self.section.course.last_item_get_content_time = datetime.now()

        item_content = self._get_content(root)
        item_raw_html = response.text
        videos = None
        choices = None

        if self.is_video:
            videos = self._fetch_item_video()
        if self.is_choice:
            choice = Choice(answers=None, item=self)
            answers = [Answer(choice=choice, **i) for i in get_answers(root)]
            choice.answers = answers

        return {
            "videos": videos,
            "content": item_content,
            "raw_html": item_raw_html,
            "choice": choice,
        }

    def _should_wait_for_request(self) -> bool:
        """
        Devuelve True si es necesario esperar antes de hacer la siguiente solicitud.
        """
        if self.section.course.last_item_get_content_time is None:
            return False

        diff_time = datetime.now() - self.section.course.last_item_get_content_time
        if diff_time.total_seconds() < 15:
            return True
        return False

    def _wait_for_request(self):
        """
        Pausa el programa si es necesario esperar antes de hacer la siguiente solicitud.
        """
        randint = random.randint(5, 30)
        utils.sleep_program(randint)
        self.section.course.last_item_get_content_time = datetime.now()

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

    def mark_as_watched(self):
        if self.is_video and not self.is_marked_as_seen:
            self._make_request(self.url)

            url_api = f"{self.url}/mark-video"
            course_code = Path(urlparse(self.url).path).parent.parent.name
            data = {
                "courseCode": course_code,
                "videoTaskId": self.taks_id,
            }
            response = self._make_request(url=url_api, method="POST", data=data)
            if response.reason is "OK":
                self.is_marked_as_seen = True
        elif self.is_choice and not self.is_marked_as_seen:
            content = self.get_content()
            choice = content["choice"]
            answers = [answer for answer in choice.answers if answer.is_correct]
            choice.send_answers(answers)

    @property
    def taks_id(self) -> str:
        return Path(urlparse(self.url).path).name

    @property
    def is_video(self) -> bool:
        return self.type == utils.ArticleType.VIDEO

    @property
    def is_choice(self) -> bool:
        return self.type.is_choice
