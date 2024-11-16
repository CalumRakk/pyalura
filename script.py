from pyalura.alura import Alura

url = "https://app.aluracursos.com/course/java-trabajando-lambdas-streams-spring-framework/task/87011"
alura = Alura(url)

for course in alura.iter_course():
    print(course)
