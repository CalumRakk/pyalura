import logging
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import parse_qs, urljoin, urlparse

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
    """
    Representa un elemento individual dentro de una sección del curso, que puede ser un video, tarea, etc.

    Esta clase se encarga de obtener, gestionar y manipular la información
    de un elemento específico, ya sea su contenido, videos asociados o respuestas a preguntas.

    Atributos:
        url (str): URL del elemento.
        title (str): Título del elemento.
        index (str): Índice del elemento dentro de la sección.
        type (ArticleType): Tipo del elemento (video, tarea, etc.).
        section (Section): Sección a la que pertenece el elemento.
        is_marked_as_seen (bool): Indica si el elemento ha sido marcado como visto.
    """

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

        logger.debug(f"Item creado: {self.title} ({self.url})")

    @property
    def course(self) -> "Course":
        return self.section.course

    def get_content(self) -> dict:
        """
        Obtiene el contenido del episodio/tarea del curso.

        Esto incluye el contenido en formato markdown, videos asociados (si los hay),
        y las opciones de respuestas (si son preguntas de opción múltiple).

        Returns:
            dict: Un diccionario con el contenido del item, videos, respuestas y el HTML original.
                *   `videos`: Un diccionario con la información de los videos del item (si es un video).
                *   `content`: El contenido del item en formato markdown.
                *   `raw_html`: El HTML original del item.
                *   `choice`: Un objeto Question con las opciones de respuesta (si es una tarea).
        """
        logger.info(f"Solicitando el contenido del item")
        if self._should_wait_for_request():
            self._wait_for_request()

        response = self._make_request(self.url)
        root = html.fromstring(response.text)

        self.section.course.last_item_get_content_time = datetime.now()

        item_content = self._get_content(root)
        item_raw_html = response.text
        videos = None
        question = None

        if self.is_video:
            videos = self._fetch_item_video()
        if self.is_question:
            question = Question(
                answers=None, item=self
            )  # TODO: revisar si answers debe ser opcional
            answers = [
                Answer(choice=question, **i) for i in Answer.parse_from_html(root)
            ]
            question.answers = answers
            logger.debug(
                f"Obtenida la información de las respuestas para el item: {self.title}"
            )

        logger.info(f"Contenido obtenido exitosamente.")
        return {
            "videos": videos,
            "content": item_content,
            "raw_html": item_raw_html,
            "question": question,
        }

    def _should_wait_for_request(self) -> bool:
        """
        Verifica si se debe esperar antes de realizar una solicitud.

        Comprueba si ha pasado suficiente tiempo desde la última solicitud al backend.
        Esto se utiliza para no saturar el servidor de Alura con peticiones.

        Returns:
            bool: True si debe esperar, False en caso contrario.
        """
        if self.section.course.last_item_get_content_time is None:
            logger.debug(
                f"No se requiere esperar, no hay registro de última petición para el item: {self.title}"
            )
            return False

        diff_time = datetime.now() - self.section.course.last_item_get_content_time
        wait_condition = diff_time.total_seconds() < 15
        logger.debug(
            f"Validando si se requiere esperar para el item: {self.title}. Condición: {wait_condition}"
        )
        return wait_condition

    def _wait_for_request(self):
        """
        Pausa la ejecución del programa durante un tiempo aleatorio.

        Esta pausa ayuda a evitar saturar el servidor con múltiples peticiones en un corto periodo.
        """
        randint = random.randint(5, 30)
        logger.debug(
            f"Esperando {randint} segundos antes de realizar la petición al servidor para el item: {self.title}"
        )
        utils.sleep_progress(randint)
        self.section.course.last_item_get_content_time = datetime.now()

    def _is_video_expired(self, video_url: str) -> bool:
        """
        Verifica si la URL del video ha expirado.

        Analiza la URL del video y comprueba si la fecha de expiración ha sido alcanzada.

        Args:
            video_url (str): URL del video a verificar.

        Returns:
            bool: True si la URL ha expirado, False en caso contrario.
        """
        logger.debug(f"Verificando si la url del video: {video_url} ha expirado")
        url_parsed = urlparse(video_url)
        query_params = {
            key: value[0] for key, value in parse_qs(url_parsed.query).items()
        }
        expires = int(query_params["X-Amz-Expires"])
        request_time = datetime.strptime(query_params["X-Amz-Date"], "%Y%m%dT%H%M%SZ")
        expired = datetime.utcnow() - request_time >= timedelta(seconds=expires)
        logger.debug(f"Resultado de verificación de expiración del video: {expired}")
        return expired

    def _fetch_item_video(self) -> dict:
        """
        Obtiene la información de los videos asociados a un elemento.

        Realiza una petición a la API para obtener la información de los videos, incluyendo diferentes calidades.

        Returns:
            dict: Un diccionario con la información de los videos.
        """
        logger.info(
            f"Obteniendo información de los videos del item: {self.title} ({self.url})"
        )
        url_api = f"{urljoin('https://app.aluracursos.com/', self.url)}/video"
        response = self._make_request(url_api)
        videos = response.json()
        videos = {i["quality"]: i for i in videos}
        logger.debug(
            f"Información de los videos para el item: {self.title} obtenida correctamente"
        )
        return videos

    def _get_content(self, root) -> str:
        """
        Extrae el contenido HTML del elemento y lo convierte a formato Markdown.

        Busca el elemento HTML que contiene el contenido principal de la tarea y lo convierte a Markdown.

        Args:
            root (html.HtmlElement): El elemento raíz del HTML del item.

        Returns:
            str: El contenido del item en formato Markdown.
        Raises:
            ValueError: Si no se encuentra el contenido del item.
        """
        logger.debug(
            f"Extrayendo contenido HTML a Markdown del item: {self.title} ({self.url})"
        )
        element = root.find(".//section[@id='task-content']")
        if element is None:
            logger.error(
                f"No se encontró el contenido de la tarea para el item: {self.title} ({self.url})"
            )
            raise ValueError(
                f"No se encontró el contenido de la tarea para el item: {self.title}"
            )
        header = root.find(".//span[@class='task-body-header-title-text']").text.strip()
        content = html.tostring(element)
        markdown_content = self._convert_html_to_markdown(
            content, header
        )  # FIX: pide bytes, pero recibe un string. Comprobar esto.
        logger.debug(f"Contenido Markdown del item: {self.title} extraído con éxito")
        return markdown_content

    def _convert_html_to_markdown(self, html_content: bytes, header: str) -> str:
        """
        Convierte un bloque de HTML a formato Markdown.

        Args:
            html_content (bytes): El contenido HTML a convertir.
            header (str): El encabezado del contenido.

        Returns:
            str: El contenido en formato Markdown con el encabezado.
        """
        logger.debug(f"Convirtiendo HTML a Markdown")
        string = html2text.html2text(html_content.decode("UTF-8"))
        return f"# {header}\n\n{string}"

    def mark_as_watched(self):
        """
        Marca un video o tarea como vista en la plataforma.

        Para videos, realiza una petición a la API para marcar el video como visto.
        Para tareas, obtiene las respuestas correctas y las envía al backend.
        """
        if self.is_marked_as_seen:
            logger.info(
                f"El item: {self.title} ya fue visto, no se puede marcar de nuevo"
            )
            return False

        if self.is_video:
            logger.info(f"Marcando el video como visto: {self.title} ({self.url})")
            self._make_request(self.url)

            url_api = f"{self.url}/mark-video"
            course_code = Path(urlparse(self.url).path).parent.parent.name
            data = {
                "courseCode": course_code,
                "videoTaskId": self.taks_id,
            }
            response = self._make_request(url=url_api, method="POST", data=data)
            if response.reason == "OK":
                self.is_marked_as_seen = True
                logger.info(f"Video: {self.title} marcado como visto con exito")
                return True
        elif self.is_question:
            logger.info(
                f'Se intento marcar como visto un Item choice, use "resolve_choice" en vez de "mark_as_watched" para el item: {self.url}'
            )
            return False
        else:
            logger.info(f"Marcando el Item como visto: {self.title} ({self.url})")
            self._make_request(self.url)
            self.is_marked_as_seen = True
            return True
        return False

    def resolve_question(self):
        if self.is_marked_as_seen is True:
            logger.info(
                f"El item: {self.title} ya fue resuelto, no se puede resolver de nuevo"
            )
            return False

        if self.is_question:
            logger.info(f"Resolviendo la pregunta: {self.title} ({self.url})")
            content = self.get_content()
            question: Question = content["question"]
            question.resolve()
            self.is_marked_as_seen = True
            return True
        logger.info(f"El item: {self.title} no es una pregunta")
        return False

    @property
    def taks_id(self) -> str:
        """
        Devuelve el ID de la tarea extraído de la URL.

        Returns:
            str: El ID de la tarea.
        """
        task_id = Path(urlparse(self.url).path).name
        logger.debug(f"Obteniendo el task_id: {task_id} del item: {self.title}")
        return task_id

    @property
    def is_video(self) -> bool:
        """
        Verifica si el elemento es de tipo video.

        Returns:
            bool: True si el elemento es un video, False en caso contrario.
        """
        is_video = self.type == utils.ArticleType.VIDEO
        logger.debug(f"Validando si el item: {self.title} es video: {is_video}")
        return is_video

    @property
    def is_question(self) -> bool:
        """
        Verifica si el elemento es de tipo choice (pregunta de opción múltiple).

        Returns:
            bool: True si el elemento es una pregunta de opción múltiple, False en caso contrario.
        """
        is_question = self.type.is_question
        logger.debug(f"Validando si el item: {self.title} es choice: {is_question}")
        return is_question

    @property
    def is_document(self) -> bool:
        """
        Verifica si el elemento es de tipo documento.

        Returns:
            bool: True si el elemento es un documento, False en caso contrario.
        """
        is_document = self.type == utils.ArticleType.is_document
        logger.debug(f"Validando si el item: {self.title} es documento: {is_document}")
        return is_document

    @property
    def is_last_item(self) -> bool:
        # Variables para detectar la posición actual del item en el curso
        if hasattr(self, "_is_last_item") is False:
            if self.section.is_last_section:
                is_last_item = self.index == self.section.index_last_section
                setattr(self, "_is_last_item", is_last_item)
        return getattr(self, "_is_last_item")

    @staticmethod
    def parse_items_from_html(root: "HtmlElement") -> list[dict]:
        """
        Devuelve una lista de diccionarios con información estructurada sobre cada item.

        Returns:
            list[dict]: Una lista de diccionarios, donde cada diccionario representa un item con los siguientes campos:
                - `url` (str): La URL completa del artículo.
                - `title` (str): El título del artículo.
                - `index` (str): El índice o número del artículo.
                - `type` (ArticleType): El tipo de artículo, como VIDEO, COMPLEMENTARY_INFORMATION, etc.

        Ejemplo de retorno:
            [
                {
                    "url": "https://app.aluracursos.com/course/java-trabajando-lambdas-streams-spring-framework/task/86876",
                    "title": "Presentación",
                    "index": "01",
                    "type": <ArticleType.VIDEO: 1>
                },
                {
                    'url': 'https://app.aluracursos.com/course/java-trabajando-lambdas-streams-spring-framework/task/86877',
                    'title': 'Un nuevo proyecto utilizando Spring Framework',
                    'index': '02',
                    'type': <ArticleType.VIDEO: 1>
                },
                ...
            ]

        Notas:
            - La función busca artículos dentro de un elemento `<ul>` con la clase `task-menu-nav-list`.
            - La URL de cada artículo se construye utilizando la base `https://app.aluracursos.com/` y el valor del atributo `href` del enlace (`<a>`).
            - El tipo de artículo (`type`) se determina a partir del valor de `xlink:href` del elemento `<use>`.
        """

        articulos = []
        for articulo in root.xpath(".//ul[@class='task-menu-nav-list']/li"):
            url = urljoin(
                "https://app.aluracursos.com/", articulo.find(".//a").get("href")
            )
            title = articulo.find(".//span[@title]").text.strip()
            index = articulo.find(
                ".//span[@class='task-menu-nav-item-number']"
            ).text.strip()
            type = getattr(
                ArticleType, articulo.find(".//use").get("xlink:href").split("#")[1]
            )
            is_marked_as_seen = "task-menu-nav-item-svg--done" in articulo.find(
                ".//svg"
            ).get("class")
            articulos.append(
                {
                    "url": url,
                    "title": title,
                    "index": index,
                    "type": type,
                    "is_marked_as_seen": is_marked_as_seen,
                }
            )

        return articulos
