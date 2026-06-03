#  Copyright (c) 2023 StatPrism Team. All rights reserved.

import qtawesome as qta
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QWidget

from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet


class OverlayPopup(QWidget):
    """Full-window dimmed overlay with a centered content panel that closes when
    the user clicks anywhere outside the panel (same UX as the data-table popup)."""

    def __init__(self, anchor_widget, content: QWidget):
        window = anchor_widget.window()
        super().__init__(window, Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setGeometry(window.rect())

        self._overlay = QWidget(self)
        self._overlay.setGeometry(self.rect())
        set_stylesheet(self._overlay, css(background_color="rgba(0,11,22,0.4)"))
        self._overlay.show()

        self.content = content
        self.content.setParent(self)
        # Clicks on the panel itself must not close the popup.
        self.content.mousePressEvent = lambda event: event.accept()
        self.content.adjustSize()
        self.content.move(
            (self.width() - self.content.width()) // 2,
            (self.height() - self.content.height()) // 2,
        )
        self.content.raise_()

        self.raise_()
        self.show()

    def mousePressEvent(self, event):
        if not self.content.geometry().contains(event.position().toPoint()):
            self.close()


def show_value_mapping_popup(anchor_widget, unique_values, reference_value) -> OverlayPopup:
    """Centered preview showing each value mapped to its inverted (reference - value)."""
    content = QFrame()
    set_stylesheet(content, css(background="white", border="1px solid gray"))
    grid = QGridLayout(content)
    grid.setContentsMargins(12, 12, 12, 12)

    for i, value in enumerate(unique_values):
        label_left = QLabel(str(value), content)
        label_left.setFont(Style.font_regular)
        label_left.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        label_center = QLabel(content)
        label_center.setPixmap(qta.icon("mdi.arrow-right", color="black").pixmap(20, 20))
        label_center.setFixedWidth(20)

        label_right = QLabel(str(reference_value - value), content)
        label_right.setFont(Style.font_regular)
        label_right.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        grid.addWidget(label_left, i, 0)
        grid.addWidget(label_center, i, 1)
        grid.addWidget(label_right, i, 2)

    return OverlayPopup(anchor_widget, content)
