import enum
import json
import logging
import random
import time
from pathlib import Path
from typing import TYPE_CHECKING, Union
from urllib.parse import urljoin, urlparse

import unidecode

if TYPE_CHECKING:
    from pyalura.item import Item

import re

from lxml.html import HtmlElement

caracteres_invalidos = re.compile('[<>:"/\\|?*\x00-\x1f]')


def string_to_slug(string):
    slug = unidecode.unidecode(string.strip())
    slug_lower = slug.lower().replace(" ", "-")
    slut_lower_sin_caracteres_invalidos = caracteres_invalidos.sub("_", slug_lower)
    return slut_lower_sin_caracteres_invalidos.rstrip(" .")


def sleep_progress(seconds):
    logger.info(f"Esperando {seconds} segundos antes de continuar...")
    for i in range(int(seconds), 0, -1):
        time.sleep(1)
        logger.debug(f"Esperando {i} segundos antes de continuar...")
    logger.debug("Continuando...")


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
    logger.debug(f"Extrayendo URL base de: {url}")

    if type(url) != str:
        raise TypeError("Se esperaba como url string")

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
    PRACTICE_CLASS_CONTENT = 11
    TEXT_CONTENT = 12

    @property
    def is_choice(self):
        return self in [
            ArticleType.SINGLE_CHOICE,
            ArticleType.MULTIPLE_CHOICE,
            ArticleType.PRACTICE_CLASS_CONTENT,
        ]

    @property
    def is_document(self):
        return self in [
            ArticleType.COMPLEMENTARY_INFORMATION,
            ArticleType.SETUP_EXPLANATION,
            ArticleType.HQ_EXPLANATION,
            ArticleType.SETUP_EXPLANATION,
            ArticleType.HQ_EXPLANATION,
            ArticleType.WHAT_WE_LEARNED,
            ArticleType.COMPLEMENTARY_INFORMATION,
            ArticleType.DO_AFTER_ME,
            ArticleType.TEXT_CONTENT,
        ]


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


def download_item(item: "Item", folder_output: Path, track_downloads=False):
    
    logger.info(f"Procesando Item: {item.index} - {item.title}")
    folder_output = (
        Path(folder_output) if isinstance(folder_output, str) else folder_output
    )

    track_downloads_path = Path("track_downloads.json")
    downloaded_items = set()

    if track_downloads and track_downloads_path.exists():
        try:
            downloaded_items = set(json.loads(track_downloads_path.read_text()))
        except json.JSONDecodeError:
            logger.warning(
                "El archivo track_downloads.json está corrupto. Se usará uno nuevo."
            )

    if track_downloads and item.url in downloaded_items:
        logger.info(f"El item ya ha sido descargado según el archivo de seguimiento.")
        return

    # Construcción de rutas
    course_path = folder_output / item.course.subcategory / item.course.title_slug
    section_path = course_path / f"{item.section.index}-{item.section.title_slug}"
    item_path = section_path / f"{item.index}-{item.title_slug}"

    # Crear directorios antes de definir la salida
    item_path.parent.mkdir(parents=True, exist_ok=True)

    if item_path.exists():
        logger.info("El item ya ha sido descargado.")
        if track_downloads:
            downloaded_items.add(item.url)
            track_downloads_path.write_text(
                json.dumps(list(downloaded_items), indent=2)
            )
        return

    # Descarga del contenido
    content = item.get_content()

    if item.is_video:
        output = item_path.with_suffix(".mp4")
        download_url = content["videos"]["hd"]["mp4"]

        response = item._make_request(download_url)

        if response.status_code != 200:
            logger.error(f"Error al descargar {item.title}: {response.status_code}")
            return

        output.write_bytes(response.content)
    else:
        output = item_path.with_suffix(".md")
        output.write_text(content["content"], encoding="utf-8")

    sleep_progress(random.randint(5, 15))
    if track_downloads:
        downloaded_items.add(item.url)
        track_downloads_path.write_text(json.dumps(list(downloaded_items), indent=2))
