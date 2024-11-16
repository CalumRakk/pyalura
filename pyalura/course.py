from typing import Iterator
import random
from datetime import datetime, timedelta
import time


from lxml import html

from pyalura.section import Section
from pyalura.base import Base
from pyalura import utils


class Course(Base):

    def __init__(self, url):
        self.url_origin = url
        self.base_course_url = utils.extract_base_url(self.url_origin)
        self.continue_course_url = utils.add_slash(self.base_course_url) + "continue/"

    @property
    def sections(self) -> list["Section"]:
        """Lista de secciones del curso con información como nombre y URL."""
        if hasattr(self, "_course_sections") is False:
            r = self._make_request(self.continue_course_url, method="HEAD")
            url_course = r.headers["location"]
            root = self._fetch_root(url_course)
            course_sections = [
                Section(**i, course=self) for i in utils.get_course_sections(root)
            ]
            setattr(self, "_course_sections", course_sections)
        return getattr(self, "_course_sections")

    def iter_course(self) -> Iterator[dict]:
        """
        Itera sobre cada episodio/tarea del curso en una forma pausable y devuelve su información.

        Yields:
            dict: Un diccionario con información sobre el artículo, que incluye:
                - "url": URL del artículo.
                - "index": Índice del artículo en la sección.
                - "title": Título del artículo.
                - "type": Tipo de artículo (ej. VIDEO).
                - "video": Datos del video (si es un video).
                - "content": Contenido del artículo.
                - "raw_html": HTML sin procesar del artículo.
                - "section": Información de la sección del curso a la que pertenece.

        """

        for section in self.sections:
            print(f"Seccion: {section.name}")
            for item in section.items:
                print("\t", f"{item.index} {item.title} - {item.type}")
                last_request_time = datetime.now()
                content = item.get_content()
                yield content

                if not content["is_cache"]:
                    diff_time = datetime.now() - last_request_time
                    if diff_time.total_seconds() < random.randint(5, 10):
                        utils.sleep_program(random.randint(5, 30))
