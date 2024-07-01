from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QColor


class LeftAlignHeaderView(QtWidgets.QHeaderView):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setDefaultAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        self.setMouseTracking(True)  # Enable mouse tracking for hover events
        self.setSectionsClickable(True)  # From QTableWidget's init
        self.setHighlightSections(True)  # From QTableWidget's init

        self._padding = 5
        self._spacing = 5
        self._icon_height = 18

    def sectionSizeFromContents(self, logicalIndex):
        if self.model():
            headerText = self.model().headerData(logicalIndex, self.orientation(), QtCore.Qt.DisplayRole)
            headerIcons = self.model().headerData(logicalIndex, self.orientation(), QtCore.Qt.DecorationRole)
            options = self.viewOptions()
            metrics = QtGui.QFontMetrics(options.font)
            maxWidth = self.sectionSize(logicalIndex)
            rect = metrics.boundingRect(
                QtCore.QRect(0, 0, maxWidth, 5000),
                int(self.defaultAlignment()) | QtCore.Qt.TextWordWrap | QtCore.Qt.TextExpandTabs,
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
            painter.save()
            self.model().hideHeaders()
            QtWidgets.QHeaderView.paintSection(self, painter, rect, logicalIndex)
            self.model().unhideHeaders()
            painter.restore()

            headerText = self.model().headerData(logicalIndex, self.orientation(), QtCore.Qt.DisplayRole)
            headerIcons = self.model().headerData(logicalIndex, self.orientation(), QtCore.Qt.DecorationRole)

            modelIndex = self.model().index(0, logicalIndex)
            if self.selectionModel().isSelected(modelIndex):
                painter.fillRect(QtCore.QRectF(rect), QColor(210, 210, 230))
            else:
                painter.fillRect(QtCore.QRectF(rect), QColor(240, 240, 250))

            painter.save()
            painter.setPen(QtGui.QPen(QColor(170, 170, 200)))
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

            painter.drawText(QtCore.QRectF(rect_padded), QtCore.Qt.TextWordWrap, headerText)
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
