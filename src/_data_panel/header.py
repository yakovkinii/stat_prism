#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import logging

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtGui import QColor

from src._data_panel.model import DataModel
from src.common.constant import COLORS, COLORS_SELECTION


class LeftAlignHeaderView(QtWidgets.QHeaderView):
    mouse_up = QtCore.Signal()

    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setDefaultAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignBottom)
        self.setMouseTracking(True)  # Enable mouse tracking for hover events
        self.setSectionsClickable(True)  # From QTableWidget's init
        self.setHighlightSections(True)  # From QTableWidget's init

        self._padding = 5
        self._spacing = 5
        self._icon_height = 18

        self.full_height = True

    def sectionSizeFromContents(self, logicalIndex):
        if self.model():
            headerText = self.model().headerData(logicalIndex, self.orientation(), QtCore.Qt.ItemDataRole.DisplayRole)
            headerIcons = self.model().headerData(
                logicalIndex, self.orientation(), QtCore.Qt.ItemDataRole.DecorationRole
            )
            metrics = QtGui.QFontMetrics(self.font())
            maxWidth = self.sectionSize(logicalIndex)

            if self.full_height:
                rect = metrics.boundingRect(
                    QtCore.QRect(0, 0, maxWidth, 5000),
                    int(self.defaultAlignment()) | QtCore.Qt.TextFlag.TextWordWrap | QtCore.Qt.TextFlag.TextExpandTabs,
                    headerText,
                    4,
                )
            else:
                rect = metrics.boundingRect(
                    QtCore.QRect(0, 0, maxWidth, 5000),
                    int(self.defaultAlignment()) | QtCore.Qt.TextFlag.TextExpandTabs,
                    headerText,
                    4,
                )

            if len(headerIcons) > 0:
                rect_expanded = rect.adjusted(
                    -self._padding, -self._padding, self._padding, self._padding + self._icon_height + self._spacing
                )
            else:
                rect_expanded = rect.adjusted(-self._padding, -self._padding, self._padding, self._padding)

            return rect_expanded.size()
        else:
            return QtWidgets.QHeaderView.sectionSizeFromContents(self, logicalIndex)

    def paintSection(self, painter, rect, logicalIndex):
        if self.model():
            model: DataModel = self.model()  # this is ok
            painter.save()
            model.hideHeaders()
            QtWidgets.QHeaderView.paintSection(self, painter, rect, logicalIndex)
            model.unhideHeaders()
            painter.restore()

            headerText = model.headerData(logicalIndex, self.orientation(), QtCore.Qt.ItemDataRole.DisplayRole)
            headerIcons = model.headerData(logicalIndex, self.orientation(), QtCore.Qt.ItemDataRole.DecorationRole)
            headerColor = model.get_column_color(logicalIndex)

            if self.selectionModel().isColumnSelected(logicalIndex):
                if headerColor is not None:
                    painter.fillRect(QtCore.QRectF(rect), QColor(COLORS_SELECTION[headerColor]))
                else:
                    painter.fillRect(QtCore.QRectF(rect), QColor("#ddd"))
                # painter.fillRect(QtCore.QRectF(rect), QColor(210, 210, 230))
            else:
                if headerColor is not None:
                    painter.fillRect(QtCore.QRectF(rect), QColor(COLORS[headerColor]))
                else:
                    painter.fillRect(QtCore.QRectF(rect), QColor("#eee"))

                # painter.fillRect(QtCore.QRectF(rect), QColor(240, 240, 250))

            painter.save()
            painter.setPen(QtGui.QPen(QColor(200, 200, 200, 100)))
            painter.drawLine(rect.topRight(), rect.bottomRight())
            painter.restore()
            if len(headerIcons) > 0:
                iconRect = QtCore.QRect(
                    rect.left() + self._padding,
                    rect.bottom() - self._icon_height - self._padding,
                    self._icon_height,
                    self._icon_height,
                )
                for headerIcon in headerIcons:
                    headerIcon.paint(painter, iconRect)
                    iconRect.setLeft(iconRect.left() + self._icon_height + self._spacing)
                    iconRect.setWidth(self._icon_height)
                # headerIcon.paint(painter, iconRect)
            if len(headerIcons) > 0:
                rect_padded = QtCore.QRectF(
                    rect.adjusted(
                        self._padding, self._padding, -self._padding, -self._padding - self._icon_height - self._spacing
                    )
                )

            else:
                rect_padded = QtCore.QRectF(rect.adjusted(self._padding, self._padding, -self._padding, -self._padding))

            painter.drawText(QtCore.QRectF(rect_padded), QtCore.Qt.TextFlag.TextWordWrap, headerText)
        else:
            QtWidgets.QHeaderView.paintSection(self, painter, rect, logicalIndex)

    def enterEvent(self, event):
        index = self.logicalIndexAt(event.pos())
        if index >= 0:
            text = self.model().headerData(index, self.orientation())
            QtWidgets.QToolTip.showText(event.globalPos(), text)
        super().enterEvent(event)

    def leaveEvent(self, event):
        QtWidgets.QToolTip.hideText()
        super().leaveEvent(event)

    def mouseMoveEvent(self, event):
        index = self.logicalIndexAt(event.pos())
        if index >= 0:
            text = self.model().headerData(index, self.orientation())
            globalPos = self.mapToGlobal(event.pos())
            QtWidgets.QToolTip.showText(globalPos, text)
        super().mouseMoveEvent(event)

    def mouseDoubleClickEvent(self, event):
        index = self.logicalIndexAt(event.pos())
        if index >= 0:
            logging.info("emitting edit_column_name")
            self.full_height = not self.full_height
            for section in range(self.count()):
                self.resizeSection(section, self.sectionSize(section) + 1)
                self.resizeSection(section, self.sectionSize(section) - 1)

    def mouseReleaseEvent(self, event):
        self.mouse_up.emit()
        super().mouseReleaseEvent(event)
