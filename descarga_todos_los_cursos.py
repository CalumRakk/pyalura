import json
from datetime import datetime, timedelta
from pathlib import Path

from pyalura import Course
from pyalura.utils import sleep_progress

URLTEXT = """https://app.aluracursos.com/course/consultas-sql-mysql
"""

URLs = URLTEXT.split("\n")
folder = "Descargas"

for url in set(URLs):
    cursos_descargados = []
    output = Path(folder) / "cursos_descargados.json"
    if output.exists():
        cursos_descargados = json.loads(output.read_text())

    if url in cursos_descargados or url == "":
        continue

    curso = Course(url)
    for section in curso.sections:
        for item in section.items:
            item.section.course.last_item_get_content_time = datetime.now() - timedelta(
                days=1
            )
            item.download(folder)
        sleep_progress(3)

    cursos_descargados.append(url)
    output.write_text(json.dumps(cursos_descargados))
