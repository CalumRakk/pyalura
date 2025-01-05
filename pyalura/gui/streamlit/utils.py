import streamlit as st
from pyalura import Course
from pathlib import Path
from pyalura.utils import ArticleType
from pydm import PyDM
import time


SUFFIX_MP4 = ".mp4"
SUFFIX_MD = ".md"


def get_file_icon(file_type):
    """Retorna el emoji correspondiente según el tipo de archivo"""
    icons = {
        "py": "🐍",  # Python
        "txt": "📄",  # Texto
        "pdf": "📕",  # PDF
        "doc": "📘",  # Word
        "docx": "📘",  # Word
        "md": "📘",  # Word
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
        file_type.lower().replace(".", ""), "📎"
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
            curse_path = Path(st.session_state.folder_output) / curso.title_slug
            curse_path.mkdir(parents=True, exist_ok=True)

            for section in curso.sections:
                indent = "&nbsp;" * (4 * level)
                st.write(
                    f"{indent}{get_file_icon('folder')} **{section.index}-{section.title_slug}/**",
                    unsafe_allow_html=True,
                )
                section_path = curse_path / f"{section.index}-{section.title_slug}"
                section_path.mkdir(parents=True, exist_ok=True)

                for item in section.items:
                    indent = "&nbsp;" * (4 * 1)
                    if item.type == ArticleType.VIDEO:
                        suffix = SUFFIX_MP4
                        icon = get_file_icon(suffix)
                    else:
                        suffix = SUFFIX_MD
                        icon = get_file_icon(suffix)

                    item_path = section_path / f"{item.index}-{item.title_slug}"
                    output = item_path.with_suffix(suffix)

                    if item._should_wait_for_request():
                        st.toast("Pausa de un par de segundos...", icon="🔄")
                    content = item.get_content()
                    if not content["is_cache"]:
                        msg = st.toast(f"{item.index}-{item.title_slug}", icon="🔄")

                    st.write(
                        f"{indent}{icon} {item.index}-{item.title_slug}",
                        unsafe_allow_html=True,
                    )

                    if not output.exists() and suffix == SUFFIX_MD:
                        output.write_text(content["content"])
                        st.toast(f"Descargado: {output.name[:19]}...", icon=icon)

                    elif not output.exists() and suffix == SUFFIX_MP4:
                        download_drr = content["videos"]["hd"]["mp4"]
                        st.toast(f"Descargando: {output.name[:19]}...", icon="🔄")

                        pydm = PyDM(download_drr, output=output, folder_temp="temp")
                        pydm.download()

                        output.with_suffix(SUFFIX_MD).write_text(content["content"])
                        msg.toast(f"Descargado: {output.name[:19]}...", icon=icon)

        st.session_state.btn_task = True
