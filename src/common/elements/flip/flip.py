import qtawesome as qta
from PySide6 import QtGui, QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QWidget

from src.common.elements.base.base import BasePanelElement
from src.common.size import Font


class InvertVisualizer(BasePanelElement):
    def __init__(self):
        super().__init__()
        self.children = []
        self.layout = None

        self.font = QtGui.QFont("Segoe UI")
        self.font.setPointSize(Font.size)

    def setup(self):
        self.widget = QWidget(self.parent_widget)
        self.layout = QGridLayout(self.widget)

    def configure(self, unique_values, max_plus_min):
        # clear layout
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().deleteLater()

        self.children = []
        for i, value in enumerate(unique_values):
            label_left = QtWidgets.QLabel(self.widget)
            label_left.setText(str(value))
            label_left.setFont(self.font)
            label_left.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            label_center = QtWidgets.QLabel(self.widget)
            icon = qta.icon("mdi.arrow-right", color="black")
            label_center.setPixmap(icon.pixmap(32, 32))
            label_center.setFixedWidth(32)

            label_right = QtWidgets.QLabel(self.widget)
            label_right.setText(str(max_plus_min - value))
            label_right.setFont(self.font)
            label_right.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

            self.children.append(label_left)
            self.children.append(label_center)
            self.children.append(label_right)

            self.layout.addWidget(label_left, i, 0)
            self.layout.addWidget(label_center, i, 1)
            self.layout.addWidget(label_right, i, 2)
