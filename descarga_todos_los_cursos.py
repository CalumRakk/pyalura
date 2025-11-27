import json
from datetime import datetime, timedelta
from pathlib import Path

from pyalura import Course
from pyalura.downloader import Downloader
from pyalura.utils import sleep_progress

URLTEXT = """https://app.aluracursos.com/course/comandos-dml-manipulacion-datos-mysql
"""

URLs = URLTEXT.split("\n")
folder = "Descargas"
downloader = Downloader(base_folder=folder)

for url in set(URLs):
    cursos_descargados = []
    output = Path(folder) / "cursos_descargados.json"
    if output.exists():
        cursos_descargados = json.loads(output.read_text())

    if url in cursos_descargados or url == "":
        continue

    curso = Course(url, cookies_path="app.aluracursos.com_cookies.txt")
    for section in curso.sections:
        for item in section.items:
            item.section.course.last_item_get_content_time = datetime.now() - timedelta(
                days=1
            )
            downloader.download_item(item)
        sleep_progress(3)

    cursos_descargados.append(url)
    output.write_text(json.dumps(cursos_descargados))
