from typing import Optional

import PySide6
from PySide6 import QtWidgets, QtGui, QtCore
import pyqtgraph as pg


class BoxPlotItem(pg.GraphicsObject):
    def __init__(
        self,
        x_value: int,
        q1: float,
        q3: float,
        median: float,
        lower_whisker: float,
        upper_whisker: float,
        pen: QtGui.QPen,
        brush: QtGui.QBrush,
    ):
        super().__init__()

        self.x_value = x_value
        self.q1 = q1
        self.q3 = q3
        self.median = median
        self.lower_whisker = lower_whisker
        self.upper_whisker = upper_whisker
        self.pen = pen
        self.brush = brush

        self.picture = None
        self.generatePicture()

    def generatePicture(self):
        self.picture = QtGui.QPicture()
        painter = QtGui.QPainter(self.picture)
        painter.setPen(self.pen)
        painter.setBrush(self.brush)

        # Box representing IQR
        painter.drawRect(QtCore.QRectF(self.x_value - 0.2, self.q1, 0.4, self.q3 - self.q1))

        # Median line
        painter.drawLine(
            QtCore.QPointF(self.x_value - 0.2, self.median), QtCore.QPointF(self.x_value + 0.2, self.median)
        )

        # Whiskers
        painter.drawLine(QtCore.QPointF(self.x_value, self.lower_whisker), QtCore.QPointF(self.x_value, self.q1))
        painter.drawLine(QtCore.QPointF(self.x_value, self.q3), QtCore.QPointF(self.x_value, self.upper_whisker))

        # Whisker caps
        painter.drawLine(
            QtCore.QPointF(self.x_value - 0.1, self.lower_whisker),
            QtCore.QPointF(self.x_value + 0.1, self.lower_whisker),
        )
        painter.drawLine(
            QtCore.QPointF(self.x_value - 0.1, self.upper_whisker),
            QtCore.QPointF(self.x_value + 0.1, self.upper_whisker),
        )

        painter.end()

    def paint(
        self,
        painter: PySide6.QtGui.QPainter,
        option: PySide6.QtWidgets.QStyleOptionGraphicsItem,
        widget: Optional[PySide6.QtWidgets.QWidget] = ...,
    ) -> None:
        if self.picture is None:
            self.generatePicture()
        painter.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QtCore.QRectF(self.picture.boundingRect())
