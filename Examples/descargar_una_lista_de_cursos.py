from pyalura import Course
from pyalura.utils import sleep_progress, download_item
from pathlib import Path
import json

URLs = [
    "https://app.aluracursos.com/course/java-trabajando-lambdas-streams-spring-framework",
    "https://app.aluracursos.com/course/spring-framework-challenge-foro-hub",
    "https://app.aluracursos.com/course/java-persistencia-datos-consultas-spring-data-jpa",
    "https://app.aluracursos.com/course/java-api-conectandola-front-end",
    "https://app.aluracursos.com/course/java-trabajando-lambdas-streams-spring-framework",
    "https://app.aluracursos.com/course/java-persistencia-datos-consultas-spring-data-jpa",
    "https://app.aluracursos.com/course/java-api-conectandola-front-end",
    "https://app.aluracursos.com/course/challenge-spring-boot-literalura",
    "https://app.aluracursos.com/course/spring-boot-3-desarrollar-api-rest-java",
    "https://app.aluracursos.com/course/spring-boot-3-aplique-practicas-proteja-api-rest",
]
folder = "Descargas"

for url in set(URLs):
    cursos_descargados = []
    output = Path(folder) / "cursos_descargados.json"
    if output.exists():
        cursos_descargados = json.loads(output.read_text())

    if url in cursos_descargados:
        continue

    curso = Course(url)
    for section in curso.sections:
        for item in section.items:
            result = download_item(item, folder)
            if result["is_downloaded"]:
                sleep_progress(25)

    cursos_descargados.append(url)
    output.write_text(json.dumps(cursos_descargados))
