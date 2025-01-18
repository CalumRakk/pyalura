from pyalura import Course
from pyalura.utils import sleep_progress
import requests
from pathlib import Path
import random
import logging


logger = logging.getLogger(__name__)
url = "https://app.aluracursos.com/course/spring-boot-3-aplique-practicas-proteja-api-rest"
curso = Course(url)

config = {"folder_output": "Descargas"}
curse_path = Path(config["folder_output"]) / curso.title_slug
for section in curso.sections:
    section_path = curse_path / f"{section.index}-{section.title_slug}"
    for item in section.items:
        item_path = section_path / f"{item.index}-{item.title_slug}"
        content = item.get_content()

        item_path.parent.mkdir(parents=True, exist_ok=True)
        if item.is_video:
            output = item_path.with_suffix(".mp4")
            if not output.exists():
                download_drr = content["videos"]["hd"]["mp4"]
                response = requests.get(
                    url=download_drr, headers=curso.cookie_manager.headers
                )
                output.write_bytes(response.content)
                sleep_progress(random.randint(15, 35))
            else:
                logger.info(f"Video {item_path} ya descargado")
        else:
            output = item_path.with_suffix(".md")
            if not output.exists():
                output.write_text(content["content"])
                sleep_progress(random.randint(15, 10))
            else:
                logger.info(f"Archivo {item_path} ya descargado")

        sleep_progress(5)
