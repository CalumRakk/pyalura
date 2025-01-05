import logging
from typing import Iterator, Union
from datetime import datetime
from urllib.parse import urljoin

from pyalura.section import Section
from pyalura.item import Item
from pyalura.base import Base
from pyalura import utils
from pyalura.utils import HOST

# Configuración del logger para este módulo
logger = logging.getLogger(__name__)


class Course(Base):
    """
    Representa un curso en la plataforma Alura.

    Esta clase se encarga de gestionar la información principal del curso,
    como su URL, secciones, y el acceso a los items del mismo.

    Atributos:
        url_origin (str): La URL original del curso.
        base_course_url (str): La URL base del curso.
        continue_course_url (str): La URL para continuar el curso.
        title (str): El título del curso extraído de la URL.
    """

    def __init__(self, url: str):
        self.url_origin = url
        self.base_course_url = utils.extract_base_url(self.url_origin)
        self.continue_course_url = utils.add_slash(self.base_course_url) + "continue/"
        self.title = utils.extract_name_url(self.url_origin)

        logger.debug(f"Course inicializado con URL: {self.url_origin}")
        super().__init__()

    @property
    def sections(self) -> list["Section"]:
        """
        Devuelve la lista de secciones del curso.

        Si la lista de secciones no ha sido cargada previamente, la obtiene del backend.

        Returns:
            list[Section]: Lista de objetos Section que componen el curso.
        """
        if not hasattr(self, "_course_sections"):
            logger.debug(f"Obteniendo secciones del curso: {self.title}")
            r = self._make_request(self.continue_course_url, method="HEAD")
            url_course = r.headers["location"]

            if r.headers.get("location") is None:
                logger.info(f"El curso '{self.title}' no ha sido iniciado.")
                logger.debug(f"Intentando iniciar el curso '{self.title}'...")
                path_tryToEnroll = f"/courses/{self.title}/tryToEnroll"
                url_tryToEnroll = urljoin(HOST, path_tryToEnroll)
                r2 = self._make_request(url_tryToEnroll, method="HEAD")
                url_course = r2.headers["location"]

            root = self._fetch_root(url_course)
            page_title = root.find(".//title").text.strip()
            logger.debug(f"Título de la página: {page_title}")

            course_sections = [
                Section(**i, course=self) for i in utils.get_course_sections(root)
            ]
            logger.debug(
                f"Secciones del curso: {len(course_sections)}, primer elemento: {course_sections[0].__dict__}"
            )
            setattr(self, "_course_sections", course_sections)
        return getattr(self, "_course_sections")

    @property
    def last_item_get_content_time(self) -> Union[datetime, None]:
        """
        Devuelve la fecha y hora de la última llamada al método get_content() de un Item.

        Returns:
            Union[datetime, None]: La fecha y hora de la última llamada, o None si no hay registro.
        """
        if not hasattr(self, "_last_item_get_content_time"):
            return None
        return getattr(self, "_last_item_get_content_time")

    @last_item_get_content_time.setter
    def last_item_get_content_time(self, value: Union[datetime, None]):
        """
        Establece la fecha y hora de la última llamada al método get_content() de un Item.

        Args:
            value (Union[datetime, None]): La fecha y hora a establecer.
        Raises:
            TypeError: Si el valor proporcionado no es un objeto datetime o None.
        """
        if not isinstance(value, datetime) and value is not None:
            raise TypeError("El valor debe ser un objeto datetime o None")

        setattr(self, "_last_item_get_content_time", value)
        logger.debug(f"Estableciendo last_item_get_content_time a: {value}")
        return getattr(self, "_last_item_get_content_time")

    def iter_items(self) -> Iterator["Item"]:
        """
        Itera sobre todos los items (episodios/tareas) del curso.

        Yields:
            Item: Cada uno de los items del curso.
        """
        logger.debug(f"Iterando sobre los items del curso: {self.title}")
        for section in self.sections:
            for item in section.items:
                logger.debug(
                    f"Yielding item: {item.taks_id} de la sección: {section.index} del curso: {self.title}"
                )
                yield item
