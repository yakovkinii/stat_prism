#  Copyright (c) 2023 StatPrism Team. All rights reserved.
from PySide6 import QtCore
from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QWidget,
)

from src.pyside_ext.markup import css
from src.pyside_ext.unique_qss import set_stylesheet


def view_widget_in_popup(parent, widget, handler_on_close):
    WidgetPopup(parent, widget, handler_on_close)


class WidgetPopup(QWidget):
    def __init__(self, parent, widget, handler_on_close):
        super().__init__(parent, QtCore.Qt.FramelessWindowHint)
        self.widget = widget
        self.handler_on_close = handler_on_close
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        # self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setGeometry(parent.rect())

        overlay = QWidget(self)
        overlay.setGeometry(self.rect())
        set_stylesheet(overlay, css(background_color="rgba(0,11,22,0.4)"))
        overlay.show()
        # make overlay oblique to mouse events
        overlay.mousePressEvent = lambda e: e.accept()

        self.popup = QFrame(self)
        w, h = int(parent.width() * 0.95), int(parent.height() * 0.95)
        self.popup.setFixedSize(w, h)
        self.popup.move((parent.width() - w) // 2, (parent.height() - h) // 2)
        set_stylesheet(self.popup, css(background="white"))
        self.popup.mousePressEvent = lambda e: e.accept()

        self.popup_layout = QVBoxLayout(self.popup)
        self.popup_layout.setContentsMargins(0, 0, 0, 0)
        self.popup_layout.setSpacing(0)

        self.padding_widget = QWidget(self.popup)
        self.padding_layout = QVBoxLayout(self.padding_widget)
        self.padding_layout.setContentsMargins(5, 5, 5, 5)
        self.padding_layout.setSpacing(0)

        self.padding_layout.addWidget(self.widget)
        self.popup_layout.addWidget(self.padding_widget)
        self.show()

    def mousePressEvent(self, event):
        if not self.popup.geometry().contains(event.position().toPoint()):
            self.close()
            self.handler_on_close()
            event.accept()
        else:
            event.ignore()

