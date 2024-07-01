from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QTableView, QAbstractItemView, QHeaderView


class DataView(QTableView):
    def __init__(self, parent=None):
        super(DataView, self).__init__(parent)
        palette = self.palette()
        palette.setColor(QPalette.Highlight, QColor(240, 240, 240))  # Change to the color you want
        palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
        self.setPalette(palette)

        # self.setStyleSheet("""
        #     QTableView {
        #         selection-background-color: rgb(245, 245, 245);
        #         selection-color: black;
        #     }
        # """)
    def wheelEvent(self, event):
        if event.angleDelta().y() != 0 and self.horizontalHeader().underMouse():
            # Translate vertical scrolling to horizontal
            delta = event.angleDelta().y() / 100
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta)
            event.accept()  # Accept the event to prevent default handling
        else:
            super().wheelEvent(event)  # Default behavior for other cases
