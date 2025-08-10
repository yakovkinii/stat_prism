#  Copyright (c) 2023 StatPrism Team. All rights reserved.

from PySide6.QtCore import QObject, Qt, QThread, Signal
from PySide6.QtWidgets import QApplication, QProgressDialog, QPushButton, QVBoxLayout, QWidget, QProgressBar


class Worker(QObject):
    progress = Signal(int)
    finished = Signal(object)
    canceled = Signal()

    def __init__(self, func):
        super().__init__()
        self.func = func
        self._running = True

    def stop(self):
        self._running = False

    def run(self):
        def update_progress(value):
            self.progress.emit(value)
            if not self._running:
                raise Exception("Cancelled")

        try:
            result = self.func(update_progress)
        except Exception:
            self.canceled.emit()
            return
        self.finished.emit(result)


def with_progress(func, steps=100, parent=None, title="Working...", on_done=None):
    dlg = QProgressDialog(title, "Cancel", 0, steps, parent)
    dlg.setWindowTitle("Progress")
    dlg.setWindowModality(Qt.WindowModal)
    dlg.setMinimumDuration(0)

    thread = QThread()
    worker = Worker(func)
    worker.moveToThread(thread)

    worker.progress.connect(dlg.setValue)
    worker.finished.connect(
        lambda result: (thread.quit(), thread.wait(), dlg.close(), on_done(result) if on_done else None)
    )
    worker.canceled.connect(lambda: (thread.quit(), thread.wait(), dlg.close()))

    dlg.canceled.connect(lambda: worker.stop())

    thread.started.connect(worker.run)
    thread.start()


def with_progress_bar(func, progress_bar: QProgressBar, steps=100, on_done=None):
    progress_bar.setRange(0, steps)
    progress_bar.setValue(0)

    thread = QThread()
    worker = Worker(func)
    worker.moveToThread(thread)

    worker.progress.connect(progress_bar.setValue)
    worker.finished.connect(lambda result: (thread.quit(), thread.wait(), on_done(result) if on_done else None))
    worker.canceled.connect(lambda: (thread.quit(), thread.wait()))
    # cancel_button.clicked.connect(worker.stop)

    thread.started.connect(worker.run)
    thread.start()


# --- Heavy work example ---
def compute_heavy_stuff(update):
    try:
        for i in range(10):
            for _ in range(50_000_000):
                pass  # Simulated heavy loop
            update(i * 10)  # Manual progress update
    except Exception as e:
        return f"Task was cancelled or failed: {e}"
    return "Done!"


# --- GUI Application ---
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Progress Threaded API Demo")
        layout = QVBoxLayout(self)

        button = QPushButton("Start Heavy Task")
        button.clicked.connect(self.run_task)
        layout.addWidget(button)

    def run_task(self):
        with_progress(compute_heavy_stuff, steps=100, parent=self, on_done=self.on_done)
        print("launched")

    def on_done(self, result):
        print("Computation result:", result)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
