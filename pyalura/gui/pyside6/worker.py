from PySide6.QtCore import QObject, Signal
import time


class Worker(QObject):
    progress = Signal(str)
    finished = Signal()

    def run_job(self):
        for _ in range(5):
            self.progress.emit(f"Cargando ...")
            time.sleep(1)
        self.progress.emit(f"")
        self.finished.emit()
