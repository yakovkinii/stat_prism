from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtWidgets import QLineEdit, QTextEdit

from src.common.constant import DEBUG_LAYOUT


class EditableLabel(QLineEdit):
    def __init__(self, parent):
        super().__init__(parent)

        self.setStyleSheet("border: none; background-color: rgba(255,255,255,100);")
        if DEBUG_LAYOUT:
            self.setStyleSheet("border: 1px solid blue; background-color: #eef;")

        self.setCursorPosition(0)
        self.editingFinished.connect(self.editing_finished)

    def editing_finished(self):
        self.setCursorPosition(0)
        self.clearFocus()


class EditableLabelWordwrap(QTextEdit):
    editingFinished = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.setFixedWidth(388)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet("border: none; background-color: rgba(255,255,255,100);")
        if DEBUG_LAYOUT:
            self.setStyleSheet("border: 1px solid blue; background-color: #eef;")
        self.textChanged.connect(self.adjustHeightToFitText)
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == event.KeyPress:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                self.clearFocus()  # will emit editingFinished
                return True
        return super().eventFilter(obj, event)

    def focusOutEvent(self, event):
        self.editingFinished.emit()
        super().focusOutEvent(event)

    def text(self):
        return self.toPlainText()

    def adjustHeightToFitText(self):
        doc = self.document()
        doc.setTextWidth(388.0)
        self.setFixedHeight(doc.size().height() + 2 * self.frameWidth())

    def scheduleAdjustHeightToFitText(self):
        QTimer.singleShot(10, self.adjustHeightToFitText)
