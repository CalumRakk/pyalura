from pyalura import Course

url = "https://app.aluracursos.com/course/java-trabajar-listas-colecciones-datos/task/86025"
item = Course.get_item(url)  # Instancia una clase especifica que contiene una pregunta
content = item.get_content()  # Obtiene el contenido de la pregunta
choice = content["choice"]  # Obtiene la pregunta

print(content["content"])
answer = choice.answers[1].select()  # Marca la respuesta 1 como correcta.
choice.send_answers(answer)  # Envia la respuesta seleccionada al backend
