# PyAlura

Esta es una API no oficial para interactuar con la plataforma de Alura

## Instalación

```sh
pip install git+https://github.com/CalumRakk/pyalura
```

## Guía de inicio rápido

Para comenzar a utilizar esta API, siga las instrucciones a continuación.

Lo primero es obtener la Cookies de Alura. Puedes utilizar cualquier extension como [Get cookies.txt LOCALLY
](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc). Una vez que hayas instalado la extensión, sigue estos pasos:

1. Dirígete a [Alura](https://app.aluracursos.com/)
2. Haz clic en el icono de la extensión en la barra del navegador.
3. Selecciona la opción de exportar para copiar las cookies.
4. Guarda las cookies en un archivo llamado cookies.json.




importar la clase `Course`

    from pyalura import Course

```python
from pyalura import Course

url = "https://app.aluracursos.com/course/spring-framework-challenge-foro-hub"
curso = Course(url)
for section in curso.sections:
    for item in section.items:
        print("url:", item.url)
        print("title:", item.title)
        print("is_marked_as_seen:", item.is_marked_as_seen)

```
