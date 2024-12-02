from PySide6.QtWidgets import (
    QApplication,
    QVBoxLayout,
    QWidget,
    QLineEdit,
    QPushButton,
    QLabel,
    QSizePolicy,
    QFrame,
    QTreeWidget,
    QTreeWidgetItem,
    QHeaderView,
    QProgressBar,
    QLayout,
)

from PySide6.QtCore import Qt, QThread
from PySide6.QtCore import Slot
import sys
from pyalura.gui.pyside6.worker import Worker
from pyalura import Course


class CustomButton(QPushButton):
    def __init__(self, text, parent):
        super().__init__(text)

        self.parent = parent
        self.setObjectName("primary")
        self.setStyleSheet(
            """*, QPushButton#primary {
                background-color: rgb(255, 255, 255);
                border: 1.2px solid rgba(49, 51, 63, 0.2);
                color: rgb(49, 51, 63);
                line-height: 1.6;
                padding: 8px 16px;
                border-radius: 4px;
                text-transform: uppercase;
                font-weight: 500;
                
            }
            QPushButton#primary:hover {
                border-color: rgb(255, 75, 75);
                color: rgb(255, 75, 75);
            }
            QPushButton#primary:pressed {
                color: rgb(255, 255, 255);
                border-color: rgb(255, 75, 75);
                background-color: rgb(255, 75, 75);          
            }
            QPushButton#disabled {                
                color: #fff;
                background-color: #6c757d;
                border-color: #6c757d;
                
            }
            """
        )
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.enabled = True
        self.clicked.connect(self.button_clicked)

    @property
    def main_window(self):
        return self.parent.main_window

    def enterEvent(self, event):
        """Cambia el cursor al pasar sobre el botón."""
        if not self.enabled:
            self.setCursor(Qt.CursorShape.ForbiddenCursor)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Restaura el cursor al salir del botón."""
        self.setCursor(Qt.CursorShape.ArrowCursor)
        super().leaveEvent(event)

    def button_clicked(self):
        # Deshabilitar el botón durante la ejecución

        if self.enabled is False:
            return

        # Crear el hilo y el self.worker
        url = self.parent.url_input.text()
        self.worker = Worker(url)
        self.thread: QThread = QThread()
        # Mover el self.worker al hilo creado, para que no se ejecute en el hilo principal
        self.worker.moveToThread(self.thread)

        # Conectar señales y slots
        self.thread.started.connect(self.toggle_enabled)
        self.thread.started.connect(self.worker.run_job)
        self.worker.progress.connect(
            lambda msg: self.main_window.size_label.setText(msg)
        )
        self.worker.result.connect(self.main_window.add_to_layout_tree_widget)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.toggle_enabled)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # Iniciar el hilo
        self.thread.start()
        print("Proceso iniciado")

    @Slot()
    def toggle_enabled(self):
        self.enabled = not self.enabled
        self.setObjectName("disabled" if self.enabled is False else "primary")
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()


class LayoutURL(QVBoxLayout):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        self.init_ui()

    def init_ui(self):
        """Inicia la interfaz de usuario del LayoutURL."""
        # Crear un QLineEdit para ingresar la URL
        self.url_input = self.create_url_input()
        self.download_button = CustomButton("Descargar", self)

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


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Downloader")
        self.setStyleSheet("background-color: white;")
        self.resize(900, 600)

        # Configurar layout principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.init_ui(self.main_layout)
        self.main_layout.setContentsMargins(15, 0, 15, 0)
        self.main_layout.setSpacing(10)

    def init_ui(self, main_layout: QLayout):
        """Inicia la interfaz de usuario del MainWindow."""
        # Título
        self.h1 = self.create_title_label()
        main_layout.addWidget(self.h1)

        # Layout para URL
        layout_url = LayoutURL(main_window=self)
        main_layout.addLayout(layout_url)

        # Spacer: Empuja el footer hacia la parte inferior
        main_layout.addStretch()

        # Footer
        footer = self.create_footer()
        main_layout.addWidget(footer)

        main_layout.setContentsMargins(5, 0, 5, 0)

    def create_title_label(self):
        """Crea y configura el título de la ventana."""
        h1 = QLabel("📂 Descargar cursos de Alura")
        h1.setStyleSheet("font-size: 24px; font-weight: bold;")
        h1.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        return h1

    def create_footer(self):
        """Crea y configura el pie de página."""
        footer = QFrame(self)
        footer.setStyleSheet(
            "color: #505050; background-color: #f0f0f0; padding: 0 10 0 10px;"
        )
        footer_layout = QVBoxLayout(footer)

        self.size_label = QLabel()
        self.size_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )

        footer_layout.addWidget(self.size_label)
        return footer

    @Slot(Course)
    def add_to_layout_tree_widget(self, course: Course, index_layout: int = 2):
        tree_widget = QTreeWidget()
        tree_widget.setHeaderLabels(["Elementos", "Progreso"])
        tree_widget.setStyleSheet("border: none;")
        tree_widget.header().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        tree_widget.header().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        tree_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        tree_widget.setContentsMargins(50, 0, 15, 0)

        # curse_path = Path(st.session_state.folder_output) / curso.title_slug
        # curse_path.mkdir(parents=True, exist_ok=True)
        folder_structure = {}
        for section in course.sections:
            folder_icon = "📁"
            section_name = f"{folder_icon} {section.index}-{section.title_slug}"
            folder_structure[section_name] = []
            for item in section.items:
                item_name = f"{item.index}-{item.title_slug}"
                folder_structure[section_name].append(item_name)

        folder_structure = {"📁 Curso": folder_structure}
        for folder_curse, folders in folder_structure.items():
            ifolder_curse = QTreeWidgetItem(tree_widget, [folder_curse])
            ifolder_curse.setExpanded(True)
            for folder, files in folders.items():
                ifolder = QTreeWidgetItem(ifolder_curse, [folder])
                ifolder.setExpanded(True)
                # tree_widget.addTopLevelItem(ifolder)
                for file_name in files:
                    progress_bar = QProgressBar()
                    progress_bar.setValue(0)
                    progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    file_item = QTreeWidgetItem(ifolder, [file_name])
                    ifolder.addChild(file_item)
                    tree_widget.setItemWidget(file_item, 1, progress_bar)

        tree_widget.expandAll()
        self.main_layout.insertWidget(index_layout, tree_widget, stretch=2)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
