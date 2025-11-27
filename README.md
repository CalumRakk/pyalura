# PyAlura 🦉

> **Una API no oficial de Python elegante y potente para interactuar, automatizar y descargar contenido de la plataforma Alura Latam.**

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)]()

**PyAlura** te permite abstraerte de la complejidad de la navegación web y tratar los cursos, secciones y actividades como objetos nativos de Python.

## Características

- **Descarga masiva:** Baja cursos completos (videos en HD y lecturas en Markdown) con una sola línea de código.
- **Automatización:** Completa actividades, marca clases como vistas y responde cuestionarios automáticamente.
- **Gestión inteligente:** Control de historial para no descargar lo mismo dos veces y retardos automáticos para simular comportamiento humano.
- **API Orientada a Objetos:** Accede a `Course`, `Section` e `Item` de forma intuitiva.

---

## Instalación

Instala directamente desde el repositorio:

```bash
pip install git+https://github.com/CalumRakk/pyalura
```

---

## 🍪 Configuración (Cookies)

Para acceder a tu cuenta, PyAlura necesita tus cookies de sesión exportadas en formato **Netscape**.

1. Instala la extensión **[Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)** en tu navegador.
2. Loguéate en Alura y exporta las cookies.
3. Guarda el archivo como `cookies.txt` en la misma carpeta donde ejecutarás tus scripts.

> **Nota:** El script buscará automáticamente archivos como `cookies.txt`, `cookies.json` o `app.aluracursos.com_cookies.txt`, pero no te fies en esto. Es mejor especificar la ubicacion de las cookies en la clase `Course(..., cookies_path="cookies.txt")`.

---

## 🚀 Uso Rápido


### 1. Descargar Cursos Completos

El `Downloader` se encarga de crear carpetas, gestionar duplicados y guardar videos y texto.

```python
from pyalura.downloader import Downloader

# 1. Define dónde guardarás los cursos
downloader = Downloader(base_folder="Mis Cursos Alura")

# 2. Descarga un curso individual
downloader.download_course("https://app.aluracursos.com/course/spring-boot-3-aplique-practicas-proteja-api-rest")

# 3. O descarga una lista entera
lista_cursos = [
    "https://app.aluracursos.com/course/python-data-science-primeros-pasos",
    "https://app.aluracursos.com/course/comandos-dml-manipulacion-datos-mysql"
]
downloader.download_list(lista_cursos)
```

### 2. Completar Actividades Automáticamente

¿Necesitas ponerte al día? PyAlura puede recorrer el curso, ver los videos y resolver los cuestionarios por ti.

```python
from pyalura import Course

url = "https://app.aluracursos.com/course/java-trabajar-listas-colecciones-datos/"
course = Course(url)

# Magia: Recorre todo el curso, ve videos y responde preguntas.
course.complete_all_activities()
```

---

## Uso Avanzado (API de bajo nivel)

Si necesitas un control granular para crear tus propios scripts personalizados, puedes acceder directamente a la estructura del curso.

```python
from pyalura import Course

course = Course("https://app.aluracursos.com/course/ejemplo")

print(f"Curso: {course.title}")

# Iterar manualmente sobre la estructura
for section in course.sections:
    print(f"\nSección {section.index}: {section.title}")
    
    for item in section.items:
        status = "✅" if item.is_marked_as_seen else "⭕"
        type_icon = "🎥" if item.is_video else "📝"
        
        print(f"   {status} {type_icon} {item.title}")
        
        # Puedes interactuar con items individuales
        # item.get_content()
        # item.mark_as_watched()
```

### Responder una pregunta específica

```python
from pyalura import Course

# URL directa a una tarea tipo "pregunta"
url_pregunta = "https://app.aluracursos.com/course/java-collections/task/86025"
item = Course.get_item(url_pregunta)

# Resuelve la pregunta automáticamente basándose en la lógica interna
item.resolve_question()
```

