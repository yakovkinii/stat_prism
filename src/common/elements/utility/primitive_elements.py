#
#  Copyright (c) 2024 Ivan I. Yakovkin. All rights reserved.
#

from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import QEvent, Qt, QTimer, Signal
from PySide6.QtWidgets import QFrame, QLabel, QTextEdit

from src.common.unique_qss import set_stylesheet


class QWidgetClickable(QFrame):
    clicked = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


class QListWidgetClickable(QtWidgets.QListWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self.reasonable_number_of_columns = 6
        self.height = 18

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.parent().mousePressEvent(event)

    def sizeHint(self):
        return QtCore.QSize(20, self.calculate_height())

    def minimumSizeHint(self):
        return self.sizeHint()

    def calculate_height(self):
        new_height = self.height * self.reasonable_number_of_columns + 2
        if self.horizontalScrollBar().isVisible():
            new_height += self.horizontalScrollBar().height()
        return new_height


class QLabelClickable(QLabel):
    clicked = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


class EditableLabelWordwrap(QTextEdit):
    editingFinished = Signal(bool)

    def __init__(self, parent):
        super().__init__(parent)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        set_stylesheet(self, "#id{" "border: 1px solid grey;" "background-color: rgba(255,255,255,255);" "}")
        self.textChanged.connect(self.adjustHeightToFitText)
        self.installEventFilter(self)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.accept_editing = True

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self.clearFocus()  # will emit editingFinished
                return True

            if event.key() == Qt.Key.Key_Escape:
                self.accept_editing = False
                self.clearFocus()
                return True
        return super().eventFilter(obj, event)

    def focusInEvent(self, event):
        self.accept_editing = True
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        self.editingFinished.emit(self.accept_editing)
        super().focusOutEvent(event)

    def text(self):
        return self.toPlainText()

    def adjustHeightToFitText(self):
        doc = self.document()
        doc.setTextWidth(self.width())
        self.setFixedHeight(int(doc.size().height() + 2 * self.frameWidth()))

    def scheduleAdjustHeightToFitText(self):
        QTimer.singleShot(10, self.adjustHeightToFitText)
