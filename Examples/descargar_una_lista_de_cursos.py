from pyalura import Course
from pyalura.utils import download_item

URLs = [
    "https://app.aluracursos.com/course/oracle-cloud-infrastructure-base-datos-infraestructura-codigo",
    "https://app.aluracursos.com/course/python-data-science-primeros-pasos",
    "https://app.aluracursos.com/course/consultas-sql-mysql",
]
folder = "Descargas"

for url in URLs:
    course = Course(url)
    for section in course.sections:
        for item in section.items:
            download_item(item, folder)
