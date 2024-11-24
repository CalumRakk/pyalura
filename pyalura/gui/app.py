from pathlib import Path
import streamlit as st
from pyalura.gui.textarea import TextArea
from pyalura.gui.utils import display_path_tree

FOLDER_DOWNLOAD = Path("descargas")
FOLDER_DOWNLOAD.mkdir(exist_ok=True)


def main():
    st.set_page_config(
        page_title="Explorador de Archivos", page_icon="📂", layout="wide"
    )

    if "TextArea" not in st.session_state:
        st.session_state.TextArea = TextArea()

        if Path("cookies.json").exists():
            value = Path("cookies.json").read_text()
            st.session_state.TextArea.value = value
            st.session_state.TextArea.disable()

    if "btn_task" not in st.session_state:
        st.session_state.btn_task = True

    st.sidebar.header("Cookies")

    with st.container():
        input_cookies = None

        input_cookies = st.sidebar.text_area(
            "Pega las cookies aquí",
            value=st.session_state.TextArea.value,
            disabled=st.session_state.TextArea.disabled,
        )

        texto_boton = "Editar" if st.session_state.TextArea.is_disabled else "Guardar"

        if st.sidebar.button(texto_boton, disabled=not st.session_state.btn_task):
            if input_cookies and texto_boton == "Guardar":
                Path("cookies.json").write_text(input_cookies)
                st.session_state.TextArea.value = input_cookies
                st.session_state.TextArea.toggle()
                st.rerun()
            elif input_cookies and texto_boton == "Editar":
                st.session_state.TextArea.toggle()
                st.rerun()
            else:
                st.sidebar.error("Por favor, introduce las cookies.")

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
