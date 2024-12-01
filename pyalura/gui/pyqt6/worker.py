from PyQt6.QtCore import QThread, pyqtSignal, QObject
import time


class Worker(QObject):
    progress = pyqtSignal(str)
    finished = pyqtSignal()

    def run_job(self):
        for _ in range(5):
            time.sleep(1)
            self.progress.emit(f"Cargando ...")
        self.finished.emit()
        print("Terminado")


class WorkerThread(QThread):
    def __init__(self, worker):
        super().__init__()
        self.worker = worker
