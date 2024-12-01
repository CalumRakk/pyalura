from PyQt6.QtWidgets import (
    QApplication,
    QVBoxLayout,
    QWidget,
    QLineEdit,
    QPushButton,
    QLabel,
    QSizePolicy,
    QFrame,
)
from PyQt6.QtCore import Qt
import sys


class LayoutURL(QVBoxLayout):
    def __init__(self):
        super().__init__()
        self.setContentsMargins(15, 0, 15, 0)
        self.init_ui()

    def init_ui(self):
        """Inicia la interfaz de usuario del LayoutURL."""
        # Crear un QLineEdit para ingresar la URL
        self.url_input = self.create_url_input()
        self.download_button = self.create_download_button()

        # Agregar widgets al layout
        self.addWidget(self.url_input)
        self.addWidget(self.download_button, alignment=Qt.AlignmentFlag.AlignTop)

    def create_url_input(self):
        """Crea el QLineEdit para ingresar la URL."""
        url_input = QLineEdit()
        url_input.setPlaceholderText("Ingresa la URL")
        url_input.setText(
            "https://app.aluracursos.com/course/java-trabajando-lambdas-streams-spring-framework/task/87011"
        )
        url_input.setStyleSheet(
            """QLineEdit { padding: 5px; border: 1px solid rgb(240, 242, 246);
            border-radius: 5px;
            background-color: rgb(240, 242, 246);}"""
        )
        return url_input

    def create_download_button(self):
        """Crea el botón de descarga."""
        download_button = QPushButton("Descargar")
        download_button.setStyleSheet(
            """QPushButton {
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
            }"""
        )
        download_button.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        return download_button


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Downloader")
        self.setStyleSheet("background-color: white;")
        self.resize(900, 600)

        # Configurar layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.init_ui(main_layout)

    def init_ui(self, main_layout):
        """Inicia la interfaz de usuario del MainWindow."""
        # Título
        self.h1 = self.create_title_label()
        main_layout.addWidget(self.h1)

        # Layout para URL
        layout_url = LayoutURL()
        main_layout.addLayout(layout_url)

        # Spacer: Empuja el footer hacia la parte inferior
        main_layout.addStretch()

        # Footer
        footer = self.create_footer()
        main_layout.addWidget(footer)

    def create_title_label(self):
        """Crea y configura el título de la ventana."""
        h1 = QLabel("📂 Descargar cursos de Alura")
        h1.setStyleSheet("font-size: 24px; font-weight: bold; padding: 0 15px;")
        h1.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        return h1

    def create_footer(self):
        """Crea y configura el pie de página."""
        footer = QFrame(self)
        footer.setStyleSheet(
            "color: #505050; background-color: #f0f0f0; padding: 0 15px;"
        )
        footer_layout = QVBoxLayout(footer)

        self.size_label = QLabel("Tamaño: 400 x 300")
        self.size_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )

        footer_layout.addWidget(self.size_label)
        return footer

    def resizeEvent(self, event):
        """Actualiza el tamaño de la ventana al cambiar su tamaño."""
        new_size = event.size()
        self.size_label.setText(f"Tamaño: {new_size.width()} x {new_size.height()}")
        super().resizeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
