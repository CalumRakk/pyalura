from pyalura import Course

url = "https://app.aluracursos.com/course/java-trabajando-lambdas-streams-spring-framework/task/87011"
course = Course(url)

for section in course.sections:
    print(f"Seccion: {section.name}")

    for item in section.items:
        print("\t", f"{item.index} {item.title} - {item.type}")
        content = item.get_content()
