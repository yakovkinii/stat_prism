from PyQt5.QtWidgets import QWidget, QLineEdit, QVBoxLayout, QLabel

from core.globals.debug import DEBUG_LAYOUT


class EditableLabel(QLineEdit):
    def __init__(self, parent):
        super().__init__(parent)

        self.setStyleSheet("QLineEdit { border: none; background-color: rgba(255,255,255,100); }")
        if DEBUG_LAYOUT:
            self.setStyleSheet("border: 1px solid blue; background-color: #eef;")

        self.setCursorPosition(0)
        self.editingFinished.connect(self.editing_finished)

    def editing_finished(self):
        self.setCursorPosition(0)
        self.clearFocus()