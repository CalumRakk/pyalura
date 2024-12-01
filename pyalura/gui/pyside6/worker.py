from PySide6.QtCore import QObject, Signal
import time
from pyalura import Course


class Worker(QObject):
    progress = Signal(str)
    finished = Signal()
    result = Signal(object)

    def __init__(self, url):
        self.url = url
        super().__init__()

    def run_job(self):
        self.progress.emit(f"Obteniendo contenido del curso...")
        time.sleep(5)
        course = Course(self.url)
        self.progress.emit(f"{course.title} obtenido")
        self.result.emit(course)
        self.finished.emit()
