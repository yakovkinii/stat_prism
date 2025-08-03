#  Copyright (c) 2023 StatPrism Team. All rights reserved.
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QSizePolicy, QTextBrowser


class TextBrowser(QTextBrowser):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.setFrameStyle(0)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet(
            """
            background: white;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
        """
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
