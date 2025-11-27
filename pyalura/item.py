import logging
import random
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import urljoin, urlparse

import html2text
from lxml import html
from lxml.html import HtmlElement

from pyalura import utils
from pyalura.question import Answer, Question
from pyalura.utils import ArticleType

from .base import Base

if TYPE_CHECKING:
    from pyalura.course import Course
    from pyalura.section import Section

logger = logging.getLogger(__name__)


class Item(Base):
    """Clase base para todos los elementos del curso (Documentos, etc)."""

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

        super().__init__(cookie_manager=section.cookie_manager)
        logger.debug(f"Item creado ({self.__class__.__name__}): {self.title}")

    @property
    def course(self) -> "Course":
        return self.section.course

    @property
    def taks_id(self) -> str:
        return Path(urlparse(self.url).path).name

    @property
    def is_video(self) -> bool:
        return self.type == utils.ArticleType.VIDEO

    @property
    def is_question(self) -> bool:
        return self.type.is_question

    @property
    def is_last_item(self) -> bool:
        if hasattr(self, "_is_last_item") is False:
            if self.section.is_last_section:
                is_last_item = self.index == self.section.index_last_section
                setattr(self, "_is_last_item", is_last_item)
        return getattr(self, "_is_last_item")

    def _should_wait_for_request(self) -> bool:
        if self.section.course.last_item_get_content_time is None:
            return False
        diff_time = datetime.now() - self.section.course.last_item_get_content_time
        return diff_time.total_seconds() < 15

    def _wait_for_request(self):
        randint = random.randint(5, 30)
        logger.debug(f"Esperando {randint}s antes de pedir: {self.title}")
        utils.sleep_progress(randint)
        self.section.course.last_item_get_content_time = datetime.now()

    def _convert_html_to_markdown(self, html_content: bytes, header: str) -> str:
        string = html2text.html2text(html_content.decode("UTF-8"))
        return f"# {header}\n\n{string}"

    def get_resource_stream(self, url: str):
        return self._make_request(url, stream=True)

    def get_content(self) -> dict:
        """Lógica base: obtiene HTML y lo convierte a Markdown."""
        logger.info(f"Solicitando contenido del item: {self.title}")
        if self._should_wait_for_request():
            self._wait_for_request()

        response = self._make_request(self.url)
        root = html.fromstring(response.text)
        self.section.course.last_item_get_content_time = datetime.now()

        # Extracción básica de texto
        element = root.find(".//section[@id='task-content']")
        if element is None:
            # Fallback para items que quizas no tienen task-content estandar
            logger.warning(f"No se encontró task-content en {self.title}")
            markdown_content = ""
        else:
            header = root.find(
                ".//span[@class='task-body-header-title-text']"
            ).text.strip()
            markdown_content = self._convert_html_to_markdown(
                html.tostring(element), header
            )

        return {
            "videos": None,
            "content": markdown_content,
            "raw_html": response.text,
            "question": None,
        }

    def mark_as_watched(self):
        """Lógica base: Marca como visto haciendo GET a la URL."""
        if self.is_marked_as_seen:
            logger.info(f"Item ya visto: {self.title}")
            return False

        logger.info(f"Marcando como visto (Base): {self.title}")
        self._make_request(self.url)
        self.is_marked_as_seen = True
        return True

    def resolve_question(self):
        """Por defecto un item no se puede 'resolver'."""
        logger.info(f"El item {self.title} no es una pregunta, no se hace nada.")
        return False

    @staticmethod
    def create(data: dict, section: "Section") -> "Item":
        """Factory que decide qué subclase instanciar según el tipo."""
        article_type = data.get("type")

        if article_type == utils.ArticleType.VIDEO:
            return VideoItem(**data, section=section)
        elif article_type and article_type.is_question:
            return QuestionItem(**data, section=section)
        else:
            return Item(**data, section=section)

    @staticmethod
    def parse_items_from_html(root: "HtmlElement", section: "Section") -> list["Item"]:
        """
        Parsea el HTML y retorna una lista de OBJETOS Item (o subclases).
        Nota: Ahora requiere recibir la sección para instanciar directamente.
        """
        items_objects = []
        for articulo in root.xpath(".//ul[@class='task-menu-nav-list']/li"):
            url = urljoin(
                "https://app.aluracursos.com/", articulo.find(".//a").get("href")
            )
            title = articulo.find(".//span[@title]").text.strip()
            index = articulo.find(
                ".//span[@class='task-menu-nav-item-number']"
            ).text.strip()
            type_enum = getattr(
                ArticleType, articulo.find(".//use").get("xlink:href").split("#")[1]
            )
            is_seen = "task-menu-nav-item-svg--done" in articulo.find(".//svg").get(
                "class"
            )

            data = {
                "url": url,
                "title": title,
                "index": index,
                "type": type_enum,
                "is_marked_as_seen": is_seen,
            }
            items_objects.append(Item.create(data, section))

        return items_objects


class VideoItem(Item):
    """Subclase para manejar lógica exclusiva de videos."""

    def _fetch_item_video(self) -> dict:
        url_api = f"{urljoin('https://app.aluracursos.com/', self.url)}/video"
        return self._make_request(url_api).json()

    def get_content(self) -> dict:
        content_data = super().get_content()
        videos_json = self._fetch_item_video()
        videos_formatted = {i["quality"]: i for i in videos_json}

        content_data["videos"] = videos_formatted
        return content_data

    def mark_as_watched(self):
        if self.is_marked_as_seen:
            return False

        self._make_request(self.url)
        logger.info(f"Marcando VIDEO como visto: {self.title}")
        url_api = f"{self.url}/mark-video"
        course_code = Path(urlparse(self.url).path).parent.parent.name
        data = {"courseCode": course_code, "videoTaskId": self.taks_id}

        response = self._make_request(url=url_api, method="POST", data=data)
        if response.ok:  # requests usa .ok para 200-299
            self.is_marked_as_seen = True
            return True
        return False


class QuestionItem(Item):
    """Subclase para manejar lógica exclusiva de preguntas/choice."""

    def get_content(self) -> dict:
        content_data = super().get_content()
        root = html.fromstring(content_data["raw_html"])

        question = Question(answers=None, item=self)
        answers = [Answer(choice=question, **i) for i in Answer.parse_from_html(root)]
        question.answers = answers

        content_data["question"] = question
        return content_data

    def mark_as_watched(self):
        logger.warning(f"Use 'resolve_question' para el item: {self.title}")
        return False

    def resolve_question(self):
        if self.is_marked_as_seen:
            return False

        logger.info(f"Resolviendo pregunta: {self.title}")
        # Necesitamos cargar el contenido para saber las respuestas
        content = self.get_content()
        question: Question = content["question"]

        if question and question.resolve():
            self.is_marked_as_seen = True
            return True
        return False
