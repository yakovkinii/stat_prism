from PyQt5 import QtWidgets, QtCore, QtGui


class LeftAlignHeaderView(QtWidgets.QHeaderView):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setDefaultAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.setMouseTracking(True)  # Enable mouse tracking for hover events
        self.setSectionsClickable(True)  # From QTableWidget's init
        self.setHighlightSections(True)  # From QTableWidget's init

    def paintSection(self, painter, rect, logicalIndex):
        # super().paintSection(painter, rect, logicalIndex)
        painter.save()
        text = self.model().headerData(logicalIndex, self.orientation())

        # Set elide mode to show the beginning of the text
        elidedText = painter.fontMetrics().elidedText(text, QtCore.Qt.ElideRight, rect.width())

        # Draw the text
        painter.drawText(rect, QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter, elidedText)

        # Draw right border for each section
        painter.setPen(QtGui.QPen(QtCore.Qt.lightGray))
        painter.drawLine(rect.topRight(), rect.bottomRight())

        painter.restore()
        super(LeftAlignHeaderView, self).paintSection(painter, rect, logicalIndex)

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