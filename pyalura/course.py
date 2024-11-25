from typing import Iterator, Union
from datetime import datetime
from urllib.parse import urljoin

from pyalura.section import Section
from pyalura.item import Item
from pyalura.base import Base
from pyalura import utils
from pyalura.utils import HOST
import logging

logger = logging.getLogger(__name__)


class Course(Base):

    def __init__(self, url):
        self.url_origin = url
        self.base_course_url = utils.extract_base_url(self.url_origin)
        self.continue_course_url = utils.add_slash(self.base_course_url) + "continue/"
        self.title = utils.extract_name_url(self.url_origin)

        logger.debug(f"Course: {self.url_origin}")
        super().__init__()

    @property
    def sections(self) -> list["Section"]:
        """Lista de secciones del curso con información como nombre y URL."""
        if hasattr(self, "_course_sections") is False:
            logger.debug("Fetching course sections")
            r = self._make_request(self.continue_course_url, method="HEAD")
            url_course = r.headers["location"]

            if not "continue" in url_course:
                logger.info("El curso no ha sido iniciado")
                logger.debug("Try to enroll (Iniciando Curso...)")
                path_tryToEnroll = f"/courses/{self.title}/tryToEnroll"
                url_tryToEnroll = urljoin(HOST, path_tryToEnroll)
                r2 = self._make_request(url_tryToEnroll, method="HEAD")
                url_course = r2.headers["location"]

            root = self._fetch_root(url_course)
            page_title = root.find(".//title").text.strip()
            logger.debug(f"Page title: {page_title}")

            course_sections = [
                Section(**i, course=self) for i in utils.get_course_sections(root)
            ]
            logger.debug(
                f"Course.sections: {len(course_sections)}, primer elemento: {course_sections[0].__dict__}"
            )
            setattr(self, "_course_sections", course_sections)
        return getattr(self, "_course_sections")

    @property
    def last_item_get_content_time(self) -> Union[datetime, None]:
        """Devuelve la fecha y hora de la ultima llamada a get_content()."""
        if hasattr(self, "_last_item_get_content_time") is False:
            return None
        return getattr(self, "_last_item_get_content_time")

    @last_item_get_content_time.setter
    def last_item_get_content_time(self, value):
        if not isinstance(value, datetime) and value is not None:
            raise TypeError

        setattr(self, "_last_item_get_content_time", value)
        return getattr(self, "_last_item_get_content_time")

    def iter_items(self) -> Iterator[Item]:
        """
        Itera sobre cada episodio/tarea del curso.
        """
        for section in self.sections:
            for item in section.items:
                yield item
