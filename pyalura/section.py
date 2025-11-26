import logging
from typing import TYPE_CHECKING
from urllib.parse import urljoin

from lxml.html import HtmlElement

from pyalura import utils
from pyalura.base import Base
from pyalura.item import Item

if TYPE_CHECKING:
    from pyalura import Course
logger = logging.getLogger(__name__)


class Section(Base):
    def __init__(self, name, url, course: "Course"):
        index, title = name.split(".", 1)
        self.index = index  # indice de la sección, empieza en 1.
        self.title = title.strip()
        self.url = url
        self.course = course

        super().__init__(cookie_manager=course.cookie_manager)

    @property
    def items(self) -> list[Item]:
        if hasattr(self, "_items") is False:
            root = self._fetch_root(self.url)
            items = [Item(**i, section=self) for i in Item.parse_items_from_html(root)]
            setattr(self, "_items", items)
        return getattr(self, "_items")

    @property
    def index_last_section(self) -> int:
        return self.course.index_last_section

    @property
    def is_last_section(self) -> bool:
        if hasattr(self, "_is_last_section") is False:
            is_last_section = self.index == self.index_last_section
            setattr(self, "_is_last_section", is_last_section)
        return getattr(self, "_is_last_section")

    @staticmethod
    def parse_sections_from_html(root: "HtmlElement"):
        """
        Extrae el contenido del curso desde un elemento `<select>` del HTML y devuelve una lista de secciones con sus nombres y URLs.

        Returns:
            list[dict]: Una lista de diccionarios. Cada diccionario representa una sección del curso con los siguientes campos:
                - `name` (str): El nombre de la sección.
                - `url` (str): La URL asociada a la sección.

        Ejemplo de retorno:
            [
                {
                    "name": "01. Un nuevo proyecto utilizando Spring Framework",
                    "url": "https://app.aluracursos.com/course/java-trabajando-lambdas-streams-spring-framework/section/11742/tasks"
                },
                {
                    "name": "02. Modelando los datos de la aplicación",
                    "url": "https://app.aluracursos.com/course/java-trabajando-lambdas-streams-spring-framework/section/11743/tasks"
                }
            ]
        """
        logger.debug("Obteniendo secciones del curso...")
        select_element = root.find(".//select[@class='task-menu-sections-select']")
        url_raw = select_element.get("onchange").split("=")[1].strip(";'")
        content = []
        for option_element in select_element.xpath(".//option"):
            value = option_element.get("value")
            name = option_element.text.strip()
            url_relative = url_raw.replace("'+this.value+'", value)
            url = urljoin(utils.HOST, url_relative)
            content.append({"name": name, "url": url})
        logger.debug(
            f"Secciones obtenidas: {len(content)}, primer element: {content[0]}"
        )
        return content
