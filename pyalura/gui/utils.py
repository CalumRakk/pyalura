import streamlit as st
from pyalura import Course
from pathlib import Path
from pyalura.utils import ArticleType
from pydm import PyDM
import requests_cache


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
        with st.status("Descargando curso...", expanded=True, state="running"):
            curso = Course(url)
            curse_path = Path(st.session_state.folder_output) / curso.name
            curse_path.mkdir(parents=True, exist_ok=True)

            for section in curso.sections:
                indent = "&nbsp;" * (4 * level)
                st.write(
                    f"{indent}{get_file_icon('folder')} **{section.name}/**",
                    unsafe_allow_html=True,
                )
                section_path = curse_path / section.name
                section_path.mkdir(parents=True, exist_ok=True)

                for item in section.items:
                    item_path = section_path / item.title
                    content = item.get_content()

                    icon = get_file_icon("doc")
                    if item.type == ArticleType.VIDEO:
                        icon = get_file_icon("mp4")
                        target_path = item_path.with_suffix(".mp4")
                        if not target_path.exists():
                            download_drr = content["videos"]["hd"]["mp4"]
                            with requests_cache.disabled():
                                pydm = PyDM(
                                    download_drr, output=target_path, folder_temp="temp"
                                )
                                pydm.download()

                    else:
                        target_path = item_path.with_suffix(".md")
                        if not target_path.exists():
                            target_path.write_text(content["content"])

                    indent = "&nbsp;" * (4 * 1)
                    st.write(f"{indent}{icon} {item.title}", unsafe_allow_html=True)
