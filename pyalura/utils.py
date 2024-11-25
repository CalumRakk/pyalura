import enum
from pathlib import Path
from urllib.parse import urljoin, urlparse
from datetime import timedelta
import time
import logging

from lxml.html import HtmlElement
import requests_cache
import re


def sanitize_filename(filename):
    pattern = r'[<>:"/\\|?*\x00-\x1F]'
    sanitized = re.sub(pattern, "", filename)
    sanitized = sanitized.rstrip(" .")
    return sanitized


logging.basicConfig(
    filename="log.txt",
    filemode="a",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%d-%m-%Y %I:%M:%S %p",
    level=logging.DEBUG,
    encoding="utf-8",
)

logger = logging.getLogger(__name__)
logger.info(
    """
    =====================
     Incio del programa
    ====================="""
)

requests_cache.install_cache(
    "http_cache",
    expire_after=None,
    allowable_methods=("GET", "POST", "HEAD"),
    allowable_codes=(200, 302),
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
    """
    urlparsed = urlparse(url)
    url_parts = Path(urlparsed.path).parts

    if len(url_parts) > 3:
        url_join = "/".join(url_parts[1:3])
        return urljoin(HOST, url_join)
    raise ValueError("La URL no es valida")


def extract_name_url(url):
    base_url = extract_base_url(url)
    return Path(urlparse(base_url).path).name


class ArticleType(enum.Enum):
    VIDEO = 1
    COMPLEMENTARY_INFORMATION = 2
    SETUP_EXPLANATION = 3
    SINGLE_CHOICE = 4
    DO_AFTER_ME = 5
    WHAT_WE_LEARNED = 6
    MULTIPLE_CHOICE = 7
    HQ_EXPLANATION = 8
    CHALLENGE = 9


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
        articulos.append({"url": url, "title": title, "index": index, "type": type})

    return articulos


def sleep_program(sleep_seconds: int):
    if sleep_seconds <= 0:
        return

    while sleep_seconds > 0:
        print(f"Esperando: {timedelta(seconds=sleep_seconds)}", end="\r")
        sleep_seconds -= 1
        time.sleep(1)

    last_msg = f"Esperando: {timedelta(seconds=0)}"
    print(last_msg, end="\r")
    print(" " * len(last_msg), end="\r")
