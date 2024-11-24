import json
import enum
from pathlib import Path
from urllib.parse import urljoin, urlparse
from datetime import datetime, timedelta
import time

import html2text
from lxml.html import HtmlElement
from lxml import html
import requests
import requests_cache
import logging

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
cookies = json.loads(Path("cookies.json").read_text())
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "es,es-ES;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,es-CO;q=0.5",
    # "cache-control": "no-cache",
    # "pragma": "no-cache",
    "priority": "u=0, i",
    # "referer": "https://app.aluracursos.com/course/java-trabajando-lambdas-streams-spring-framework/task/87020",
    "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Microsoft Edge";v="126"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
}


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
        url_join = "/".join(url_parts[:3])
        url_join = url_join.replace(r"//", "")
        return urljoin(HOST, url_join)
    return url


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


def fetch_item_video(item_url: str):

    url_api = f"{urljoin('https://app.aluracursos.com/', item_url)}/video"
    response = requests.get(
        url_api,
        cookies=cookies,
        headers=headers,
    )
    return response.json()


def get_item_content(root):
    element = root.find(".//section[@id='task-content']")
    header = root.find(".//span[@class='task-body-header-title-text']").text.strip()
    content = html.tostring(element)
    string = html2text.html2text(content.decode("UTF-8"))
    return f"# {header}\n\n{string}"


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
