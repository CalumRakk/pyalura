from pyalura import Course
from pyalura.utils import sleep_progress, download_item


url = "https://app.aluracursos.com/course/spring-boot-3-aplique-practicas-proteja-api-rest"
curso = Course(url)
folder = "Descargas"
for section in curso.sections:
    for item in section.items:
        download_item(item, folder)
        sleep_progress(5)
