from pyalura import Course

url = "https://app.aluracursos.com/course/spring-boot-3-aplique-practicas-proteja-api-rest"
curso = Course(url)
folder = "Descargas"
for section in curso.sections:
    for item in section.items:
        item.download(folder)
