#  Copyright (c) 2023 StatPrism Team. All rights reserved.

"""A small Android-style on/off slider switch (rounded track + knob that slides
left↔right), painted entirely in code so it needs no image assets. Colours come from
the active UI theme via Style.Color."""

from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QAbstractButton

from src.pyside_ext.styling import Style


class ToggleSwitch(QAbstractButton):
    def __init__(self, parent=None, width: int = 46, height: int = 24):
        super().__init__(parent)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._w = width
        self._h = height
        self.setFixedSize(self._w, self._h)
        self._on_color = QColor(str(Style.Color.ToggleOn.value))
        self._off_color = QColor(str(Style.Color.ToggleOff.value))
        self._knob_color = QColor(str(Style.Color.Text.value))

    def sizeHint(self) -> QSize:
        return QSize(self._w, self._h)

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        radius = self._h / 2.0
        painter.setBrush(self._on_color if self.isChecked() else self._off_color)
        painter.drawRoundedRect(QRectF(0, 0, self._w, self._h), radius, radius)

        margin = 3
        diameter = self._h - 2 * margin
        x = (self._w - diameter - margin) if self.isChecked() else margin
        painter.setBrush(self._knob_color)
        painter.drawEllipse(QRectF(x, margin, diameter, diameter))
