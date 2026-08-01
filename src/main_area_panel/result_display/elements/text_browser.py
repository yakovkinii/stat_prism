#  Copyright (C) 2023-2026  StatPrism Team
#  Balashevych A. K., Petrova N. V., Yakovkin I. I.
#
#  This file is part of StatPrism.
#
#  StatPrism is free software: you can redistribute it and/or modify it under
#  the terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  StatPrism is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with
#  StatPrism.  If not, see <https://www.gnu.org/licenses/>.

# VALIDATED

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
        # Drop the document's built-in margin so the table/text sits flush inside the
        # widget's own CSS padding (otherwise it adds an extra gap above and below the
        # content that the image-based plot element does not have).
        self.document().setDocumentMargin(0)
        set_stylesheet(
            self,
            css(
                background=Style.Color.Background,
                # Light text for the dark UI. Set on the widget (not in the HTML), so copying
                # the table to a word processor keeps the document's own (black) text color.
                color=Style.Color.Text,
                padding=Style.General.content_padding_medium,
                border=Style.General.border_elevated,
                border_radius=Style.General.border_radius_small,
            ),
        )

    def sizeHint(self) -> QSize:
        doc = self.document()
        doc.setTextWidth(self.viewport().width())

        # Small buffer so the last line / right edge is never clipped (and no scrollbar
        # appears). This used to be 24px, which left a noticeable empty band below the
        # content because this browser carries no CSS padding of its own.
        margins = self.contentsMargins()
        padding = 6

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
