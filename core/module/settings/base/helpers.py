import logging

from PyQt5.QtCore import pyqtSignal, QSizeF, QSize, QTimer, Qt
from PyQt5.QtGui import QTextOption
from PyQt5.QtWidgets import QWidget, QLineEdit, QVBoxLayout, QLabel, QTextEdit

from core.globals.debug import DEBUG_LAYOUT


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
        # self.setWordWrapMode(QTextOption.WrapAnywhere)
        self.setStyleSheet("border: none; background-color: rgba(255,255,255,100);")
        if DEBUG_LAYOUT:
            self.setStyleSheet("border: 1px solid blue; background-color: #eef;")
        self.textChanged.connect(self.adjustHeightToFitText)

    def focusOutEvent(self, event):
        self.editingFinished.emit()
        super().focusOutEvent(event)

    def text(self):
        return self.toPlainText()

    def adjustHeightToFitText(self):
        doc = self.document()
        doc.setTextWidth(388.0)

        # Translate this to python:
        #     QSizeF sz = d->pageSize;
        #     sz.setWidth(width);
        #     sz.setHeight(-1);
        #     setPageSize(sz);

        # self.document().setPageSize(QSizeF(388.0, -1))
        # self.setFixedHeight(doc.size().height() + 2 * self.frameWidth()+10)
        #

        # self.setFixedHeight(doc.size().height() + 2 * self.frameWidth() + 10)
        # height = 0
        # block = doc.begin()
        # while block.isValid():
        #     block_layout = block.layout()
        #     if block_layout:
        #         line_count = block_layout.lineCount()
        #         for i in range(line_count):
        #                 line_height = block_layout.lineAt(0).height()
        #                 height += line_height
        #             # line_height = block_layout.lineAt(0).height()
        #             # height += line_count * line_height
        #     block = block.next()
        self.setFixedHeight(doc.size().height() + 2 * self.frameWidth())
        # return height

    # def getLineHeight(self):
    #     block = self.document().firstBlock()
    #     if block.isValid():
    #         block_layout = block.layout()
    #         if block_layout and block_layout.lineCount() > 0:
    #             line = block_layout.lineAt(0)
    #             return line.height()
    #     return 0
    #
    # #
    # def adjustHeightToFitText(self):
    #     doc = self.document()
    #     doc.setTextWidth(388.0)
    #     # doc.setPageSize(QSizeF(388.0, 1000.0))
    #     # doc.adjustSize()
    #     logging.info(self.size())
    #     logging.info(doc.size())
    #
    #     newHeight = doc.size().height() + 2 * self.frameWidth()
    #     self.setMaximumHeight(newHeight)

    # def resizeEvent(self, event):
    #     super().resizeEvent(event)
    #     self.adjustHeightToFitText()

    def scheduleAdjustHeightToFitText(self):
        QTimer.singleShot(10, self.adjustHeightToFitText)
