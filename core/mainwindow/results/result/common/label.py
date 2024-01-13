from PyQt5 import QtWidgets, QtGui


class LabelClickable(QtWidgets.QLabel):
    def mousePressEvent(self, event):
        super(LabelClickable, self).mousePressEvent(event)
        event.ignore()

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        super(LabelClickable, self).resizeEvent(a0)
        self.setFixedHeight(self.sizeHint().height())

