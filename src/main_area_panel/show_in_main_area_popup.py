#  Copyright (c) 2023 StatPrism Team. All rights reserved.
from PySide6 import QtCore
from PySide6.QtWidgets import QWidget

from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet


def view_widget_in_popup(parent, widget, handler_on_close):
    return WidgetPopup(parent, widget, handler_on_close)


class WidgetPopup(QWidget):
    """Dimmed overlay covering only `parent` (so e.g. the settings panel stays usable).
    The content widget is shown at its own size, centered. Clicking the dim area (i.e.
    outside the content) closes the popup; clicking the content does not."""

    def __init__(self, parent, widget, handler_on_close):
        super().__init__(parent, QtCore.Qt.FramelessWindowHint)
        self.handler_on_close = handler_on_close
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setGeometry(parent.rect())

        # Semi-transparent dim. Not given a mousePressEvent override, so clicks on it
        # propagate up to this popup's mousePressEvent (which closes).
        self._overlay = QWidget(self)
        self._overlay.setGeometry(self.rect())
        set_stylesheet(self._overlay, css(background_color=Style.Color.Overlay))
        self._overlay.show()

        self.content = widget
        self.content.setParent(self)
        # Clicks on the content itself must not close the popup.
        self.content.mousePressEvent = lambda e: e.accept()
        self.recenter_content()
        self.content.raise_()
        self.show()
        # Take keyboard focus so Escape closes the popup (same outcome as clicking outside).
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setFocus()

    def recenter_content(self):
        """Size the content to its own size hint and center it (re-call when the
        content's size changes, e.g. after the plot is resized)."""
        self.content.adjustSize()
        self.content.move(
            max(0, (self.width() - self.content.width()) // 2),
            max(0, (self.height() - self.content.height()) // 2),
        )

    def mousePressEvent(self, event):
        if not self.content.geometry().contains(event.position().toPoint()):
            self._close_with_handler()
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self._close_with_handler()
            event.accept()
            return
        super().keyPressEvent(event)

    def _close_with_handler(self):
        self.close()
        if self.handler_on_close is not None:
            self.handler_on_close()
