#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import qtawesome as qta
from PySide6 import QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QVBoxLayout

from src.pyside_ext.elements.base import BasePanelElement
from src.pyside_ext.elements.utility.layout_helpers import empty_widget
from src.pyside_ext.styling import Style


class InvertVisualizer(BasePanelElement):
    def __init__(self):
        super().__init__()
        self.children = []
        self.layout_for_values = None

    def setup(self):
        self.widget, self.layout = empty_widget(parent=self.parent_widget, inner_layout_class=QVBoxLayout)

        self.h_widget, self.h_layout = empty_widget(
            parent=self.widget,
            outer_layout=self.layout,
            inner_layout_class=QHBoxLayout,
        )
        self.button_up = QtWidgets.QPushButton(self.h_widget)
        self.button_up.setText("Up")
        self.button_up.clicked.connect(self.on_button_up_clicked)
        self.button_down = QtWidgets.QPushButton(self.h_widget)
        self.button_down.setText("Down")
        self.button_down.clicked.connect(self.on_button_down_clicked)

        self.h_layout.addWidget(self.button_up)
        self.h_layout.addWidget(self.button_down)

        self.v_widget, self.layout_for_values = empty_widget(
            parent=self.widget,
            outer_layout=self.layout,
            inner_layout_class=QGridLayout,
        )

    def configure(self, unique_values, max_plus_min):
        self.max_plus_min = max_plus_min
        self.unique_values = unique_values
        # clear layout_for_values
        for i in reversed(range(self.layout_for_values.count())):
            self.layout_for_values.itemAt(i).widget().deleteLater()

        self.children = []
        for i, value in enumerate(unique_values):
            label_left = QtWidgets.QLabel(self.v_widget)
            label_left.setText(str(value))
            label_left.setFont(Style.font_regular)
            label_left.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            label_center = QtWidgets.QLabel(self.v_widget)
            icon = qta.icon("mdi.arrow-right", color=Style.Color.Text.value)
            label_center.setPixmap(icon.pixmap(32, 32))
            label_center.setFixedWidth(32)

            label_right = QtWidgets.QLabel(self.v_widget)
            label_right.setText(str(max_plus_min - value))
            label_right.setFont(Style.font_regular)
            label_right.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

            self.children.append(label_left)
            self.children.append(label_center)
            self.children.append(label_right)

            self.layout_for_values.addWidget(label_left, i, 0)
            self.layout_for_values.addWidget(label_center, i, 1)
            self.layout_for_values.addWidget(label_right, i, 2)

    def on_button_up_clicked(self):
        self.max_plus_min += 1
        self.configure(self.unique_values, self.max_plus_min)

    def on_button_down_clicked(self):
        self.max_plus_min -= 1
        self.configure(self.unique_values, self.max_plus_min)
