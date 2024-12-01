from PyQt6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget
import sys


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cambiar ObjectName Dinámicamente")
        self.resize(300, 200)

        layout = QVBoxLayout(self)

        self.button = QPushButton("Click para cambiar estilo")
        self.button.setObjectName("normal")  # Nombre inicial
        self.button.setStyleSheet(
            """
            QPushButton#normal {
                background-color: lightgray;
                color: black;
            }
            QPushButton#highlight {
                background-color: yellow;
                color: black;
            }
            """
        )
        self.button.clicked.connect(self.change_object_name)

        layout.addWidget(self.button)

    def change_object_name(self):
        # Cambiar el nombre del objeto dinámicamente
        if self.button.objectName() == "normal":
            self.button.setObjectName("highlight")
        else:
            self.button.setObjectName("normal")

        # Forzar la actualización del estilo
        self.button.style().unpolish(self.button)
        self.button.style().polish(self.button)
        self.button.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
