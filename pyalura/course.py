import logging
from datetime import datetime
from pathlib import Path
from typing import Iterator, Optional, Union
from urllib.parse import urljoin

import requests
from lxml import html

from pyalura import utils
from pyalura.base import Base
from pyalura.cookie_manager import CookieManager
from pyalura.item import Item
from pyalura.section import Section
from pyalura.utils import HOST, string_to_slug

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

    def __init__(self, url: str, cookies_path: Optional[Union[str, Path]] = None):
        self.url = url
        self.url_base = utils.extract_base_url(self.url)
        self.title = utils.extract_name_url(self.url)

        logger.info(f"Course instanciado con URL: {self.url}")
        super().__init__(cookies_path=cookies_path)

    def __get_course_url_button_access(self) -> bool:
        logger.debug("Obteniendo la URL del boton principal para ver el curso")
        root_base = self._get_course_page(self.url)["root"]

        has_try_to_enroll = root_base.find(".//a[@id='tryToEnroll']")
        has_data_workload = bool(
            root_base.xpath(".//a[@id='tryToEnroll' and @data-workload]")
        )
        evaluationForm = root_base.find(".//form[@id='evaluationForm']")
        if evaluationForm is not None:
            logger.info(f"El curso '{self.title}' necesita una evaluacion manual.")
            raise Exception(f"El curso '{self.title}' necesita una evaluacion manual.")

        if has_try_to_enroll and not has_data_workload:
            logger.info("El curso no es visible para el usuario.")
            raise Exception("El curso no es visible para el usuario.")

        url_relative = root_base.find(
            ".//section[@class='course']//div[@class='container']/a"
        ).get("href")
        url_botton_access = urljoin(HOST, url_relative)
        setattr(self, "_course_url_button_access", url_botton_access)
        logger.debug(f"URL obtenida: {url_botton_access}")
        return url_botton_access

    def _get_course_page(self, url: str) -> dict:
        if not hasattr(self, "__course_page"):
            logger.debug("Obteniendo la página del curso")
            response = self._make_request(url)
            root = html.fromstring(response.text)
            # la presencia de este elemento indica que el usuario esta logueado
            element_profile = root.find(".//nav[@id='profileList']")
            if element_profile is None:
                msg_error = (
                    "No se esta logueado, confirma que las cookies sean correctas"
                )
                logger.error(msg_error)
                raise Exception(msg_error)
            setattr(self, "__course_page", {"root": root, "response": response})
        return getattr(self, "__course_page")

    @property
    def subcategory(self) -> str:
        root = self._get_course_page(self.url)["root"]
        subcategory = root.find(
            ".//a[@class='course-header-banner-breadcrumb__category-link']"
        ).text.strip()
        return string_to_slug(subcategory)

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
            try:
                root = self._fetch_root(url_course)
            except Exception as e:
                logger.error(f"No se pudo obtener el contenido del curso: {e}")
                raise e

            page_title = root.find(".//title").text.strip()
            logger.info(f"Título de la página: {page_title}")

            course_sections = [
                Section(**i, course=self)
                for i in Section.parse_sections_from_html(root)
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

    @property
    def index_last_section(self) -> int:
        if hasattr(self, "_is_last_section") is False:
            index_last_section = len(self.sections) + 1
            setattr(self, "_is_last_section", index_last_section)
        return getattr(self, "_is_last_section")

    def complete_all_activities(self):
        """Recorre y completa todas las actividades pendientes."""
        logger.info(f"Completando actividades para: {self.title}")

        for item in self.iter_items():
            if item.is_marked_as_seen:
                continue

            logger.info(f"Procesando: {item.title}")

            if item.is_question:
                item.resolve_question()
                utils.sleep_progress(60)
            else:
                item.mark_as_watched()
                wait_time = 300 if item.is_video else 60
                utils.sleep_progress(wait_time)
