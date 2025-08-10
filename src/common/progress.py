from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtWidgets import QProgressBar

WORKER_COUNT = 0


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
        def update_progress(value: int):
            self.progress.emit(value)
            if not self._running:
                raise Exception("Cancelled")

        try:
            result = self.func(update_progress)
        except Exception:
            self.canceled.emit()
            return
        self.finished.emit(result)


def run_in_separate_thread(func, progress_bar: QProgressBar, steps=100, on_done=None, cancel_button=None):
    global WORKER_COUNT
    WORKER_COUNT += 1

    progress_bar.setRange(0, steps)
    progress_bar.setValue(0)
    progress_bar.setTextVisible(False)
    progress_bar.show()

    thread = QThread()
    worker = Worker(func)
    worker.moveToThread(thread)

    progress_bar._thread = thread
    progress_bar._worker = worker

    worker.progress.connect(progress_bar.setValue)

    def cleanup():
        global WORKER_COUNT
        thread.quit()
        thread.wait()
        progress_bar.hide()
        if cancel_button:
            cancel_button.setEnabled(False)
            cancel_button.clicked.disconnect(worker.stop)

        if hasattr(progress_bar, "_thread"):
            delattr(progress_bar, "_thread")
        if hasattr(progress_bar, "_worker"):
            delattr(progress_bar, "_worker")

        WORKER_COUNT -= 1

    def handle_finished(result):
        progress_bar.setValue(steps)
        cleanup()
        if on_done:
            on_done(result)

    worker.finished.connect(handle_finished)

    def handle_canceled():
        cleanup()

    worker.canceled.connect(handle_canceled)

    if cancel_button:
        cancel_button.setEnabled(True)
        cancel_button.clicked.connect(worker.stop)

    thread.started.connect(worker.run)
    thread.start()
