import enum
from pathlib import Path
from urllib.parse import urljoin, urlparse
from datetime import timedelta
import time
import random
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyalura.item import Item


from lxml.html import HtmlElement
import re


def sleep_progress(seconds):
    logger.info(f"Esperando {seconds} segundos antes de continuar...")
    for i in range(int(seconds), 0, -1):
        time.sleep(1)
        logger.debug(f"Esperando {i} segundos antes de continuar...")
    logger.debug("Continuando...")


def sanitize_filename(filename):
    pattern = r'[<>:"/\\|?*\x00-\x1F]'
    sanitized = re.sub(pattern, "", filename)
    sanitized = sanitized.rstrip(" .")
    return sanitized


logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%d-%m-%Y %I:%M:%S %p",
    level=logging.INFO,
    encoding="utf-8",
    handlers=[
        logging.FileHandler("alura.log"),  # Log a archivo
        logging.StreamHandler(),  # Log a consola
    ],
)


logger = logging.getLogger(__name__)
logger.info(
    """
    =====================
     Incio del programa
    ====================="""
)

HOST = "https://app.aluracursos.com"


def is_url_curse(url):
    # determina si la URL es la URL del curso.
    if len(Path(urlparse(url).path).parts) <= 3:
        return True
    return False


def add_slash(url):
    """
    Agrega un slash al final de la URL si no lo tiene."""
    if url[-1] != "/":
        return url + "/"
    return url


def extract_base_url(url):
    """

    Obtiene la 'URL base del curso' de una url quitando todas las subrutas de la url.

    Ejemplo:
    https://app.aluracursos.com/course/...est-java/task/83409 -> https://app.aluracursos.com/course/spring-boot-3-desarrollar-api-rest-java
    """
    urlparsed = urlparse(url)
    url_parts = Path(urlparsed.path).parts

    if len(url_parts) > 3:
        url_join = "/".join(url_parts[1:3])
        return urljoin(HOST, url_join)
    return url


def extract_name_url(url):
    base_url = extract_base_url(url)
    return Path(urlparse(base_url).path).name


class ArticleType(enum.Enum):
    """
    Enumeración de los tipos de artículos de la plataforma Alura.

    - VIDEO: El artículo es un video.
    - COMPLEMENTARY_INFORMATION: (documento de texto) El articulo es una informacion complementaria.
    - SETUP_EXPLANATION: (documento de texto) El articulo es una explicacion de configuracion.
    - SINGLE_CHOICE: (Texto con un Choice) El articulo es una pregunta de respuesta unica.
    - DO_AFTER_ME
    - WHAT_WE_LEARNED:
    - MULTIPLE_CHOICE: (Texto con un Choice) El articulo es una pregunta de respuesta multiple.
    - HQ_EXPLANATION: (documento de texto) El articulo es una explicacion de la pregunta.
    - CHALLENGE
    - LINK_SUBMIT: (Texto con un form para enviar un link) El articulo es un envio de link.
    """

    VIDEO = 1
    COMPLEMENTARY_INFORMATION = 2
    SETUP_EXPLANATION = 3
    SINGLE_CHOICE = 4
    DO_AFTER_ME = 5
    WHAT_WE_LEARNED = 6
    MULTIPLE_CHOICE = 7
    HQ_EXPLANATION = 8
    CHALLENGE = 9
    LINK_SUBMIT = 10

    @property
    def is_choice(self):
        return self in [ArticleType.SINGLE_CHOICE, ArticleType.MULTIPLE_CHOICE]


def get_course_sections(root: "HtmlElement"):
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
        url = urljoin(HOST, url_relative)
        content.append({"name": name, "url": url})
    logger.debug(f"Secciones obtenidas: {len(content)}, primer element: {content[0]}")
    return content


def get_items(root: "HtmlElement") -> list[dict]:
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
        url = urljoin("https://app.aluracursos.com/", articulo.find(".//a").get("href"))
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


def download_item(item: "Item", folder_output: Path):
    if isinstance(folder_output, str):
        folder_output = Path(folder_output)

    curso = item.section.course
    section = item.section
    curse_path = Path(folder_output) / curso.title_slug
    section_path = curse_path / f"{section.index}-{section.title_slug}"

    item_path = section_path / f"{item.index}-{item.title_slug}"
    content = item.get_content()
    item_path.parent.mkdir(parents=True, exist_ok=True)
    if item.is_video:
        output = item_path.with_suffix(".mp4")
        if not output.exists():
            download_drr = content["videos"]["hd"]["mp4"]
            response = item._make_request(download_drr)

            output.write_bytes(response.content)
            sleep_progress(random.randint(15, 35))
            return True
        else:
            logger.info(f"Video {item_path} ya descargado")
    else:
        output = item_path.with_suffix(".md")
        if not output.exists():
            output.write_text(content["content"])
            sleep_progress(random.randint(15, 10))
            return True
        else:
            logger.info(f"Archivo {item_path} ya descargado")
    return False
