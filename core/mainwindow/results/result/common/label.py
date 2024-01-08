from PyQt5 import QtWidgets


class LabelClickable(QtWidgets.QLabel):
    def mousePressEvent(self, event):
        super(LabelClickable, self).mousePressEvent(event)
        event.ignore()
