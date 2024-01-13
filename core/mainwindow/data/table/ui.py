from PyQt5 import QtWidgets


class CustomTableWidget(QtWidgets.QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def wheelEvent(self, event):
        if event.angleDelta().y() != 0 and self.horizontalHeader().underMouse():
            # Translate vertical scrolling to horizontal
            delta = event.angleDelta().y() / 100
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta)
            event.accept()  # Accept the event to prevent default handling
        else:
            super().wheelEvent(event)  # Default behavior for other cases
