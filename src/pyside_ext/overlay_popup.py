#  Copyright (c) 2023 StatPrism Team. All rights reserved.

import qtawesome as qta
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QPushButton, QWidget

from src.common.constant import PASTEL_PALETTE
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet


class OverlayPopup(QWidget):
    """Full-window dimmed overlay with a centered content panel that closes when
    the user clicks anywhere outside the panel (same UX as the data-table popup)."""

    def __init__(self, anchor_widget, content: QWidget, on_close=None):
        window = anchor_widget.window()
        super().__init__(window, Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setGeometry(window.rect())
        self._on_close = on_close

        self._overlay = QWidget(self)
        self._overlay.setGeometry(self.rect())
        set_stylesheet(self._overlay, css(background_color=Style.Color.Overlay))
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
        # Take keyboard focus so Escape closes the popup (same outcome as clicking outside).
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()

    def mousePressEvent(self, event):
        if not self.content.geometry().contains(event.position().toPoint()):
            self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
            event.accept()
            return
        super().keyPressEvent(event)

    def closeEvent(self, event):
        if self._on_close is not None:
            self._on_close()
        super().closeEvent(event)


def show_color_picker(anchor_widget, on_choose) -> OverlayPopup:
    """Centered pastel-swatch palette plus a 'None' (reset) button. Calls `on_choose(color)`
    with a hex string or None, then closes. Shared by the preprocess editor and the
    IISPWACColorPicker element."""
    holder = {}
    content = QFrame()
    set_stylesheet(
        content, css(background=Style.Color.BackgroundElevated, border=f"1px solid {Style.Color.BorderElevated}")
    )
    grid = QGridLayout(content)
    grid.setContentsMargins(10, 10, 10, 10)
    grid.setSpacing(6)

    def choose(color):
        on_choose(color)
        popup = holder.get("popup")
        if popup is not None:
            popup.close()

    per_row = 5
    for i, hex_color in enumerate(PASTEL_PALETTE):
        swatch = QPushButton(content)
        swatch.setFixedSize(28, 24)
        set_stylesheet(swatch, css(background=hex_color, border="1px solid gray"))
        swatch.clicked.connect(lambda _=False, c=hex_color: choose(c))
        grid.addWidget(swatch, i // per_row, i % per_row)

    none_button = QPushButton("None", content)
    none_button.clicked.connect(lambda _=False: choose(None))
    grid.addWidget(none_button, (len(PASTEL_PALETTE) // per_row) + 1, 0, 1, per_row)

    holder["popup"] = OverlayPopup(anchor_widget, content)
    return holder["popup"]


def show_value_mapping_popup(anchor_widget, unique_values, reference_value) -> OverlayPopup:
    """Centered preview showing each value mapped to its inverted (reference - value)."""
    content = QFrame()
    set_stylesheet(
        content, css(background=Style.Color.BackgroundElevated, border=f"1px solid {Style.Color.BorderElevated}")
    )
    grid = QGridLayout(content)
    grid.setContentsMargins(12, 12, 12, 12)

    for i, value in enumerate(unique_values):
        label_left = QLabel(str(value), content)
        label_left.setFont(Style.font_regular)
        label_left.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        label_center = QLabel(content)
        label_center.setPixmap(qta.icon("mdi.arrow-right", color=Style.Color.Text.value).pixmap(20, 20))
        label_center.setFixedWidth(20)

        label_right = QLabel(str(reference_value - value), content)
        label_right.setFont(Style.font_regular)
        label_right.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        grid.addWidget(label_left, i, 0)
        grid.addWidget(label_center, i, 1)
        grid.addWidget(label_right, i, 2)

    return OverlayPopup(anchor_widget, content)
