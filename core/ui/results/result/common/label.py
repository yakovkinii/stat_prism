from PyQt5 import QtGui, QtWidgets


class LabelClickable(QtWidgets.QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("background-color: transparent;")

    def mousePressEvent(self, event):
        super(LabelClickable, self).mousePressEvent(event)
        event.ignore()

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        super(LabelClickable, self).resizeEvent(a0)
        self.setFixedHeight(self.sizeHint().height())
