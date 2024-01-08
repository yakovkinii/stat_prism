from PyQt5 import QtCore, QtWidgets


class FrameClickable(QtWidgets.QFrame):
    clicked = QtCore.pyqtSignal()

    def __init__(self, parent):
        super(FrameClickable, self).__init__(parent)
        self.installEventFilter(self)

    def eventFilter(self, object, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            self.clicked.emit()
        return super(FrameClickable, self).eventFilter(object, event)
