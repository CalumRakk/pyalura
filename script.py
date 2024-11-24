from pyalura import Course

url = "https://app.aluracursos.com/course/java-api-conectandola-front-end"
course = Course(url)

for content in course.iter_course():
    # BUG: arreglas nombre de error.
    section = content["section"]
    print(f"Seccion: {section.name}")

    for item in section.items:
        print("\t", f"{item.index} {item.title} - {item.type}")
        content = item.get_content()
