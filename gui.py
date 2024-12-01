from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLineEdit,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QHeaderView,
    QMessageBox,
    QProgressBar,
    QSizePolicy,
    QLabel,
    QLayout,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import sys
import re  # Para validación básica de URLs
from pyalura import Course
from pathlib import Path
import time
from PyQt6.QtCore import QTimer


class Worker(QThread):
    progreso = pyqtSignal(str)

    def run(self):
        for i in range(5):
            time.sleep(1)  # Simula una tarea larga
            self.progreso.emit(f"Iteración {i + 1}/5")


class LayoutURL(QVBoxLayout):
    def __init__(self):
        super().__init__()

        # Crear un QLineEdit para ingresar la URL
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Ingresa la URL")
        self.url_input.setText(
            "https://app.aluracursos.com/course/java-trabajando-lambdas-streams-spring-framework/task/87011"
        )
        self.url_input.setStyleSheet(
            """QLineEdit { padding: 5px; border: 1px solid rgb(240, 242, 246);
            border-radius: 5px;
            background-color: rgb(240, 242, 246);}"""
        )

        # Crea boton de descarga
        self.download_button = QPushButton("Descargar")
        button_style = """QPushButton {
            background-color: transparent;
            border: 1.2px solid rgb(240, 242, 246);
            color: rgb(49, 51, 63);
            padding: 8px 16px;
            border-radius: 4px;
            text-transform: uppercase;
            font-weight: 500;
        }

        QPushButton:hover {
            border-color: rgb(255, 75, 75);
        }

        # """
        self.download_button.setStyleSheet(button_style)
        self.download_button.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        # self.download_button.clicked.connect(self.start_download)

        self.addWidget(self.url_input)
        self.addWidget(self.download_button, alignment=Qt.AlignmentFlag.AlignTop)

    # def start_download(self):
    #     url = self.url_input.text().strip()

    #     # Validar URL
    #     # if not url:
    #     #     self.show_message(
    #     #         "Error", "Por favor, ingresa una URL.", QMessageBox.Icon.Warning
    #     #     )
    #     #     return
    #     # if not self.is_valid_url(url):
    #     #     self.show_message(
    #     #         "Error",
    #     #         "La URL ingresada no es válida. Debe comenzar con http:// o https://",
    #     #         QMessageBox.Icon.Critical,
    #     #     )
    #     #     return

    #     curso = Course(url)
    #     # curse_path = Path(st.session_state.folder_output) / curso.title_slug
    #     # curse_path.mkdir(parents=True, exist_ok=True)

    #     folder_structure = {}
    #     for section in curso.sections:
    #         folder_icon = "📁"
    #         section_name = f"{folder_icon} {section.index}-{section.title_slug}"
    #         folder_structure[section_name] = []
    #         for item in section.items:
    #             item_name = f"{item.index}-{item.title_slug}"
    #             folder_structure[section_name].append(item_name)
    #     folder_structure = {"📁 Curso": folder_structure}

    #     for folder_curse, folders in folder_structure.items():
    #         ifolder_curse = QTreeWidgetItem(self.tree_widget, [folder_curse])
    #         ifolder_curse.setExpanded(True)

    #         for folder, files in folders.items():
    #             ifolder = QTreeWidgetItem(ifolder_curse, [folder])
    #             ifolder.setExpanded(True)

    #             # self.tree_widget.addTopLevelItem(ifolder)

    #             for file_name in files:
    #                 progress_bar = QProgressBar()
    #                 progress_bar.setValue(0)
    #                 progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)

    #                 file_item = QTreeWidgetItem(ifolder, [file_name])
    #                 ifolder.addChild(file_item)
    #                 self.tree_widget.setItemWidget(file_item, 1, progress_bar)

    #                 self.progress_bars.append((item, progress_bar))
    #     self.update_progress()

    # def is_valid_url(self, url):
    #     """
    #     Valida si una URL es válida.
    #     """
    #     return re.match(r"^https?://", url) is not None

    # def update_progress(self):
    #     """
    #     Actualiza dinámicamente el progreso de las barras utilizando QTimer.
    #     """
    #     self.current_index = 0  # Índice para rastrear cuál barra se está actualizando
    #     self.timer = QTimer()
    #     self.timer.timeout.connect(self.update_single_bar)
    #     self.timer.start(100)  # Actualiza cada 100 ms

    # def update_single_bar(self):
    #     """
    #     Actualiza una barra de progreso a la vez.
    #     """
    #     if self.current_index >= len(self.progress_bars):
    #         self.timer.stop()  # Detener el temporizador cuando todas las barras estén completas
    #         return

    #     item, bar = self.progress_bars[self.current_index]
    #     current_value = bar.value()
    #     if current_value < 100:
    #         bar.setValue(current_value + 10)
    #     else:
    #         bar.setValue(100)
    #         self.current_index += 1  # Pasar a la siguiente barra


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Downloader")
        self.setStyleSheet("background-color: white;")

        main_layout = QVBoxLayout(self)

        # Crea el Label
        self.h1 = QLabel()
        self.h1.setText("📂 Descargar cursos de Alura")
        self.h1.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.h1.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        main_layout.addWidget(self.h1)

        self.layout_url = LayoutURL()
        main_layout.addLayout(self.layout_url)

        # self.h1.setStyleSheet("background-color: lightblue; border: 1px solid black;")

        # lineedit = QLineEdit(main_widget)
        # lineedit.setPlaceholderText("Ingrese la URL del curso")
        # main_layout.addWidget(lineedit)

        # self.main_layout.addWidget(self.h1)
        # self.layout_url = LayoutURL()
        # self.main_layout.addLayout(self.layout_url)

        # self.layout_url = LayoutURL()
        # self.layout_url.addWidget(self.h1)
        # main_widget.setLayout(self.layout_url)

        # self.tree_widget = QTreeWidget()
        # self.tree_widget.setHeaderLabels(["", ""])
        # self.tree_widget.setStyleSheet("border: none;")
        # self.tree_widget.header().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def show_message(self, title, text, icon):
        """
        Muestra un cuadro de mensaje con un título, texto y tipo de icono.
        :param title: Título del mensaje.
        :param text: Contenido del mensaje.
        :param icon: Tipo de icono (QMessageBox.Icon).
        """
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(icon)
        msg.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
