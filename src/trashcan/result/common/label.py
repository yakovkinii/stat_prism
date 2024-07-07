from PyQt5 import QtGui, QtWidgets

from src.common.unique_qss import set_stylesheet


class LabelClickable(QtWidgets.QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        set_stylesheet(self, "#id{background-color: transparent;}")

    def mousePressEvent(self, event):
        super(LabelClickable, self).mousePressEvent(event)
        event.ignore()

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        super(LabelClickable, self).resizeEvent(a0)
        self.setFixedHeight(self.sizeHint().height())
