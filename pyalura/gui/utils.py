import streamlit as st
from pyalura import Course
import time


def get_file_icon(file_type):
    """Retorna el emoji correspondiente según el tipo de archivo"""
    icons = {
        "py": "🐍",  # Python
        "txt": "📄",  # Texto
        "pdf": "📕",  # PDF
        "doc": "📘",  # Word
        "docx": "📘",  # Word
        "xls": "📊",  # Excel
        "xlsx": "📊",  # Excel
        "csv": "📊",  # CSV
        "jpg": "🖼️",  # Imagen
        "jpeg": "🖼️",  # Imagen
        "png": "🖼️",  # Imagen
        "gif": "🖼️",  # Imagen
        "mp3": "🎵",  # Audio
        "mp4": "🎥",  # Video
        "zip": "📦",  # Comprimido
        "rar": "📦",  # Comprimido
        "folder": "📁",  # Carpeta
        "pending": "🔄",
        "done": "✅",
        "progress": "⌛",
    }
    return icons.get(
        file_type.lower(), "📎"
    )  # Icono por defecto si no se encuentra el tipo


def fetch_sections(url):
    time.sleep(5)
    course = Course(url)
    return course.sections


def display_path_tree(level=0):
    st.markdown("# 📂 Descargar cursos de Alura")
    url = st.text_input(
        "Introduce la URL:",
        value="https://app.aluracursos.com/course/java-trabajando-lambdas-streams-spring-framework/task/87011",
    )
    if "url" not in st.session_state:
        st.session_state["url"] = url

    text_boton = "Cancelar" if "task" in st.session_state else "Descargar"
    if st.button(text_boton):
        if text_boton == "Descargar":
            if st.session_state.TextArea.value is None:
                st.error("Por favor, pega las cookies")
            elif not url:
                st.error("Por favor, introduce una URL válida.")
            else:
                st.session_state.task = url
                st.session_state.btn_task = False
                st.rerun()
        else:
            del st.session_state.task
            st.session_state.btn_task = True
            st.rerun()

    st.markdown("---")

    if "task" in st.session_state:
        with st.spinner("Obtiendo informacion del curso... Por favor espera."):
            sections = fetch_sections(url)

        with st.status("Downloading data...", expanded=True, state="running"):
            for section in sections:
                indent = "&nbsp;" * (4 * level)
                st.write(
                    f"{indent}{get_file_icon('folder')} **{section.name}/**",
                    unsafe_allow_html=True,
                )

                for item in section.items:
                    icon = get_file_icon("doc")
                    indent = "&nbsp;" * (4 * 1)
                    st.write(f"{indent}{icon} {item.title}", unsafe_allow_html=True)
