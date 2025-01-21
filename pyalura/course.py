import logging
from typing import Iterator, Union
from datetime import datetime
from urllib.parse import urljoin

from pyalura.section import Section
from pyalura.item import Item
from pyalura.base import Base
from pyalura import utils
from pyalura.utils import HOST
from pyalura.cookie_manager import CookieManager
import requests
from lxml import html

# Configuración del logger para este módulo
logger = logging.getLogger(__name__)


class Course(Base):
    """
    Representa un curso en la plataforma Alura.

    Esta clase se encarga de gestionar la información principal del curso,
    como su URL, secciones, y el acceso a los items del mismo.

    Atributos:
        url (str): La URL original del curso.
        url_base (str): La URL base del curso.
        title (str): El título del curso extraído de la URL.
    """

    def __init__(self, url: str):
        self.url = url
        self.url_base = utils.extract_base_url(self.url)
        self.title = utils.extract_name_url(self.url)

        logger.info(f"Course instanciado con URL: {self.url}")
        super().__init__()

    def __get_course_url_button_access(self) -> bool:
        logger.debug("Obteniendo la URL del boton principal para ver el curso")
        root_base = self._fetch_root(self.url_base)
        url_relative = root_base.find(
            ".//section[@class='course']//div[@class='container']/a"
        ).get("href")
        url_botton_access = urljoin(HOST, url_relative)
        setattr(self, "_course_url_button_access", url_botton_access)
        logger.debug(f"URL obtenida: {url_botton_access}")
        return url_botton_access

    @property
    def sections(self) -> list["Section"]:
        """
        Devuelve la lista de secciones del curso.

        Si la lista de secciones no ha sido cargada previamente, la obtiene del backend.

        Returns:
            list[Section]: Lista de objetos Section que componen el curso.
        """
        if not hasattr(self, "_course_sections"):
            url_botton_access = self.__get_course_url_button_access()

            if url_botton_access.endswith("access"):
                logger.info(f"El curso '{self.title}' aparece como completado.")
                r_temp = self._make_request(url_botton_access, method="HEAD")
                url_botton_access = r_temp.headers["location"]
            elif url_botton_access.endswith("continue"):
                logger.info(f"El curso '{self.title}' aparece como NO completado.")
            elif url_botton_access.endswith("tryToEnroll"):
                logger.info(f"El curso '{self.title}' aparece NO iniciado.")
                r_temp = self._make_request(url_botton_access, method="HEAD")
                url_botton_access = r_temp.headers["location"]
            else:
                raise NotImplementedError

            r = self._make_request(url_botton_access, method="HEAD")
            url_course = r.headers["location"]
            root = self._fetch_root(url_course)
            page_title = root.find(".//title").text.strip()
            logger.info(f"Título de la página: {page_title}")

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
        logger.info(f"Iterando sobre los items del curso")
        for section in self.sections:
            for item in section.items:
                logger.info(
                    f"Yielding item: {item.taks_id} de la sección: {section.index} del curso: {self.title}"
                )
                yield item

    @classmethod
    def get_item(cls, item_url: str) -> "Item":
        """
        Instancia un objeto Item a partir de una URL.

        Args:
            item_url (str): La URL del item que se desea instanciar.

        Returns:
            Item: Una instancia del objeto Item correspondiente a la URL.

        Raises:
            ValueError: Si la URL no es válida o no se puede instanciar el item.
        """
        logger.info(f"Intentando instanciar un Item desde la URL: {item_url}")

        try:
            # Realizar una solicitud a la URL del item
            icookies = CookieManager()
            cookies = icookies.get_cookies()
            response = requests.get(item_url, cookies=cookies, headers=icookies.headers)
            root = html.fromstring(response.text)

            if response.status_code != 200:
                logger.warning("La solicitud no fue exitosa")
            select_selected = root.find(
                ".//select[@class='task-menu-sections-select']//option[@selected]"
            ).text
            curse = Course(item_url)
            section = Section(select_selected, item_url, curse)
            item_data = [i for i in utils.get_items(root) if i["url"] == item_url][0]
            item = Item(**item_data, section=section)
            return item

        except Exception as e:
            logger.error(f"Error al instanciar el Item desde la URL: {e}")
            raise ValueError(
                f"No se pudo instanciar el item desde la URL proporcionada: {e}"
            )
