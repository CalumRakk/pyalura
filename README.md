# PyAlura

Una API no oficial de Python para interactuar con la plataforma Alura.

## Instalación

```bash
pip install git+https://github.com/CalumRakk/pyalura
```

## Inicio rápido

1. **Obtén tus cookies de Alura:** Usa una extensión de navegador como [Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc) para exportar tus cookies a un archivo `cookies.txt`.
2. **Guarda el archivo `cookies.txt`:** Asegúrate de que el archivo `cookies.txt` esté en el mismo directorio donde ejecutarás tu script de Python.
3. **Crea una instancia de la clase `Course`:**

   ```python
   from pyalura import Course

   url_del_curso = "https://app.aluracursos.com/course/java-trabajar-listas-colecciones-datos/"
   curso = Course(url_del_curso)
   ```

4. **Accede a las secciones e items del curso:**
   ```python
   for seccion in curso.sections:
       for item in seccion.items:
           print(f"Sección: {seccion.title}, Item: {item.title}")
           contenido = item.get_content()
           # Procesa el contenido del item (videos, texto, etc.)
   ```

5. **Código completo**

    ```python
    from pyalura import Course

    url_del_curso = "https://app.aluracursos.com/course/java-trabajar-listas-colecciones-datos/"
    curso = Course(url_del_curso)
    for seccion in curso.sections:
       for item in seccion.items:
           print(f"Sección: {seccion.title}, Item: {item.title}")
           contenido = item.get_content()
    ```


## Ejemplos

### Descarga un curso completo:


```python
from pyalura import Course
from pyalura.utils import download_item

url = "https://app.aluracursos.com/course/spring-boot-3-aplique-practicas-proteja-api-rest"
curso = Course(url)
folder = "Descargas"
for section in curso.sections:
    for item in section.items:
        download_item(item, folder)

```

#### **Como responder y enviar una actividad especifica de un curso**

```python
from pyalura import Course

url = "https://app.aluracursos.com/course/java-trabajar-listas-colecciones-datos/task/86025"
item = Course.get_item(url) # Instancia una actividad especificada en la url
content = item.get_content() # Obtiene el contenido de la pregunta
question = content["question"] # Obtiene la pregunta

print(content["content"])
answer= question.answers[1].select() # Marca la respuesta 1 como correcta.
question.send_answers(answer) # Envia la respuesta seleccionada al backend
```
