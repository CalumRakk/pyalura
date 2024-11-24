from pathlib import Path
import streamlit as st
from pyalura.gui.textarea import TextArea
from pyalura.gui.utils import display_path_tree
from pyalura.cookie_manager import CookieManager
import time

FOLDER_DOWNLOAD = Path("Descargas")
FOLDER_DOWNLOAD.mkdir(exist_ok=True)
COOKIE_PATH = Path("cookies.txt")

if "btn_task" not in st.session_state:
    st.session_state.btn_task = True


def handle_cookies(cookie_path, text_area):
    """Maneja el estado de las cookies."""
    st.sidebar.header("Cookies")

    if "TextArea" not in st.session_state:
        st.session_state.TextArea = text_area
        if cookie_path.exists():
            value = cookie_path.read_text()
            st.session_state.TextArea.value = value
            st.session_state.TextArea.disable()

    input_cookies = st.sidebar.text_area(
        "Pega las cookies aquí",
        value=st.session_state.TextArea.value,
        disabled=st.session_state.TextArea.disabled,
    )

    button_text = "Editar" if st.session_state.TextArea.is_disabled else "Guardar"

    with st.sidebar:
        col1, col2 = st.columns(2)
        if col1.button(
            button_text,
            disabled=not st.session_state.btn_task,
        ):
            if input_cookies and button_text == "Guardar":
                cookie_path.write_text(input_cookies)
                st.session_state.TextArea.value = input_cookies
                st.session_state.TextArea.toggle()
                st.rerun()
            elif input_cookies and button_text == "Editar":
                st.session_state.TextArea.toggle()

                st.rerun()
            else:
                st.sidebar.error("Por favor, introduce las cookies.")

        if button_text == "Editar":
            if col2.button(
                "Validar",
                icon=":material/cookie:",
                disabled=not st.session_state.btn_task,
                use_container_width=True,
            ):
                with st.spinner("Validar Cookie..."):
                    time.sleep(1.5)
                    cookie_manager = CookieManager()
                    if cookie_manager.check_cookies():
                        st.success("Cookies validas")
                    else:
                        st.error("Cookies invalidas")


def main():
    st.set_page_config(
        page_title="Explorador de Archivos", page_icon="📂", layout="wide"
    )

    handle_cookies(COOKIE_PATH, TextArea())

    st.sidebar.markdown("---")

    with st.container():
        folder_output = st.sidebar.text_input(
            "Carpeta de descarga:",
            FOLDER_DOWNLOAD.name,
            key="folder_output",
            disabled=not st.session_state.btn_task,
        )

        if Path(st.session_state.folder_output).exists():
            st.sidebar.write(f"Has seleccionado `{folder_output}`")
        else:
            st.sidebar.write(f"No se encontro :red[{folder_output}]")

    display_path_tree()


if __name__ == "__main__":
    main()
