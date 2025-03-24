# PyAlura

Una API no oficial de Python para interactuar con la plataforma Alura.

## Instalación

```bash
pip install git+https://github.com/CalumRakk/pyalura
```

## Inicio rápido

1. **Obtén tus cookies de Alura:** Usa una extensión de navegador como [Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc) para exportar tus cookies a un archivo `cookies.txt`.

2. **Guarda el archivo `cookies.txt`:** Asegúrate de que el archivo `cookies.txt` esté en el mismo directorio donde ejecutarás tu script de Python.

3. **Crea un script en Python**

    Crea un archivo Python, por ejemplo `myscript.py`, y agrega el siguiente código para usar la clase Course e interactuar con el curso:

   ```python
   from pyalura import Course

   course_url = "https://app.aluracursos.com/course/java-trabajar-listas-colecciones-datos/"
   course = Course(course_url)
   ```

4. **Accede a las secciones e items del curso:**

   ```python
   for section in course.sections:
       for item in section.items:
           print(f"Sección: {section.title}, Item: {item.title}")
           content = item.get_content()
           # Procesa el contenido del item (videos, texto, etc.)
   ```
   
5. **Código Completo**

   A continuación, te mostramos el código completo para recorrer todas las actividades del curso e imprimir el título de cada sección y actividad en la consola.

   ```python
   from pyalura import Course

   course_url = "https://app.aluracursos.com/course/java-trabajar-listas-colecciones-datos/"
   course = Course(course_url)
   for section in course.sections:
       for item in section.items:
           print(f"Sección: {section.title}, Item: {item.title}")
   ```



## Ejemplos

### Descarga un curso completo:

El siguiente código recorre todas las activades del curso especificado y descarga todo el contenido.

```python
from pyalura import Course
from pyalura.utils import download_item

url = "https://app.aluracursos.com/course/spring-boot-3-aplique-practicas-proteja-api-rest"
course = Course(url)
folder = "Descargas"
for section in course.sections:
    for item in section.items:
        download_item(item, folder)

```

### **Como responder y enviar una actividad especifica de un curso**

El siguiente código instancia un item (actividad) especifica que contiene una pregunta y la resuelve automaticamente con solo llamar al método.

```python
from pyalura import Course

url = "https://app.aluracursos.com/course/java-trabajar-listas-colecciones-datos/task/86025"
item = Course.get_item(url)
item.resolve_question()
```

