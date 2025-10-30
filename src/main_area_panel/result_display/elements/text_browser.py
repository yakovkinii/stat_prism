#  Copyright (c) 2023 StatPrism Team. All rights reserved.
from PySide6 import QtCore
from PySide6.QtCore import QMimeData, QSize, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QSizePolicy, QTextBrowser

from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet


class TextBrowser(QTextBrowser):
    clicked = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.setFrameStyle(0)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        set_stylesheet(
            self,
            css(
                background=Style.Color.Background,
                padding=Style.General.content_padding_medium,
                border=Style.General.border_elevated,
                border_radius=Style.General.border_radius_small,
            ),
        )

    def sizeHint(self) -> QSize:
        # Calculate the document size
        doc = self.document()
        doc.setTextWidth(self.viewport().width())

        # Get margins and padding
        margins = self.contentsMargins()
        padding = 24  # Matches our CSS padding

        # Calculate total required size
        width = doc.idealWidth() + margins.left() + margins.right() + padding
        height = doc.size().height() + margins.top() + margins.bottom() + padding

        return QSize(int(width), int(height))

    def resizeEvent(self, event):
        self.updateGeometry()  # Ensure size hint is recalculated when width changes
        super().resizeEvent(event)

    def set_html(self, html: str):
        super().setHtml(html)
        self.updateGeometry()

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)  # does not propagate the event to the parent

    def contextMenuEvent(self, event):
        pass  # Disable context menu

    def copy_to_clipboard(self):
        html = self.toHtml()
        mime = QMimeData()
        mime.setHtml(html)
        QGuiApplication.clipboard().setMimeData(mime)
