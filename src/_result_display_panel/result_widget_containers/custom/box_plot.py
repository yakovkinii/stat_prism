#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from typing import Optional

import pyqtgraph as pg
import PySide6
from PySide6 import QtCore, QtGui, QtWidgets


class BoxPlotItem(pg.GraphicsObject):
    def __init__(
        self,
        x_value: int,
        q1: float,
        q3: float,
        median: float,
        lower_whisker: float,
        upper_whisker: float,
        pen1: QtGui.QPen,
        pen2: QtGui.QPen,
        brush: QtGui.QBrush,
        whiskers_only: bool,
    ):
        super().__init__()

        self.x_value = x_value
        self.q1 = q1
        self.q3 = q3
        self.median = median
        self.lower_whisker = lower_whisker
        self.upper_whisker = upper_whisker
        self.pen1 = pen1
        self.pen2 = pen2
        self.brush = brush
        self.whiskers_only = whiskers_only

        self.picture = None
        self.generatePicture()

    def generatePicture(self):
        self.picture = QtGui.QPicture()
        painter = QtGui.QPainter(self.picture)
        painter.setPen(self.pen1)
        painter.setBrush(self.brush)

        # Box representing IQR
        if not self.whiskers_only:
            painter.drawRect(QtCore.QRectF(self.x_value - 0.2, self.q1, 0.4, self.q3 - self.q1))

        painter.setPen(self.pen2)

        margin = 0

        # Whiskers
        if self.whiskers_only:
            painter.drawLine(
                QtCore.QPointF(self.x_value - 0.05 + margin, self.median),
                QtCore.QPointF(self.x_value + 0.05 - margin, self.median),
            )
            painter.drawLine(
                QtCore.QPointF(self.x_value, self.lower_whisker),
                QtCore.QPointF(self.x_value, self.upper_whisker),
            )
            painter.drawLine(
                QtCore.QPointF(self.x_value - 0.1, self.lower_whisker),
                QtCore.QPointF(self.x_value + 0.1, self.lower_whisker),
            )
            painter.drawLine(
                QtCore.QPointF(self.x_value - 0.1, self.upper_whisker),
                QtCore.QPointF(self.x_value + 0.1, self.upper_whisker),
            )
        else:
            painter.drawLine(
                QtCore.QPointF(self.x_value - 0.2 + margin, self.median),
                QtCore.QPointF(self.x_value + 0.2 - margin, self.median),
            )
            if self.lower_whisker != self.q1:
                painter.drawLine(
                    QtCore.QPointF(self.x_value, self.lower_whisker), QtCore.QPointF(self.x_value, self.q1)
                )
                painter.drawLine(
                    QtCore.QPointF(self.x_value - 0.1, self.lower_whisker),
                    QtCore.QPointF(self.x_value + 0.1, self.lower_whisker),
                )
            if self.upper_whisker != self.q3:
                painter.drawLine(
                    QtCore.QPointF(self.x_value, self.q3 + margin),
                    QtCore.QPointF(self.x_value, self.upper_whisker - margin),
                )
                painter.drawLine(
                    QtCore.QPointF(self.x_value - 0.1, self.upper_whisker),
                    QtCore.QPointF(self.x_value + 0.1, self.upper_whisker),
                )

        painter.end()

    def paint(
        self,
        painter: PySide6.QtGui.QPainter,
        option: QtWidgets.QStyleOptionGraphicsItem,
        widget: Optional[QtWidgets.QWidget] = ...,
    ) -> None:
        if self.picture is None:
            self.generatePicture()
        painter.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QtCore.QRectF(self.picture.boundingRect())
