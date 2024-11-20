#
#  Copyright (c) 2023 -- 2024 StatPrism Team. All rights reserved.
#

import qtawesome as qta
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QColorDialog,
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
)

from src.common.constant import MARKER_SHAPE_MAP
from src.common.elements.base.base import BasePanelElement
from src.common.messages import Message, MessageType
from src.common.qcolor import color_from_rgb_and_a
from src.common.result.classes.plot_result import ScatterPlotConfig


class ScatterPlotSettings(BasePanelElement):
    def __init__(self, label_text):
        self.label_text = label_text
        super().__init__()

    def setup(self):
        self.widget = QGroupBox("Scatter", self.parent_widget)
        self.layout = QVBoxLayout(self.widget)

        self.top_layout = QHBoxLayout()
        self.layout.addLayout(self.top_layout)

        self.point_color_button = QPushButton("Сolor")
        self.point_color_button.clicked.connect(self.select_color)
        self.top_layout.addWidget(self.point_color_button)

        self.marker_shape_selector = QComboBox()
        self.marker_shape_selector.addItems(list(MARKER_SHAPE_MAP.keys()))
        self.marker_shape_selector.currentTextChanged.connect(self.select_marker)
        self.top_layout.addWidget(self.marker_shape_selector)

        self.grid_layout = QGridLayout()
        self.layout.addLayout(self.grid_layout)

        self.fill_alpha_label = QLabel("Opacity:")
        self.fill_alpha_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.fill_alpha_slider = QSlider(Qt.Orientation.Horizontal)
        self.fill_alpha_slider.setMinimum(0)
        self.fill_alpha_slider.setMaximum(5)
        self.fill_alpha_slider.valueChanged.connect(self.select_fill_alpha)
        self.grid_layout.addWidget(self.fill_alpha_label, 0, 0)
        self.grid_layout.addWidget(self.fill_alpha_slider, 0, 1)

        self.line_alpha_label = QLabel("Outline:")
        self.line_alpha_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.line_alpha_slider = QSlider(Qt.Orientation.Horizontal)
        self.line_alpha_slider.setMinimum(0)
        self.line_alpha_slider.setMaximum(5)
        self.line_alpha_slider.valueChanged.connect(self.select_line_alpha)
        self.grid_layout.addWidget(self.line_alpha_label, 0, 2)
        self.grid_layout.addWidget(self.line_alpha_slider, 0, 3)

        self.jitter_x_label = QLabel("Jitter X:")
        self.jitter_x_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.jitter_x_slider = QSlider(Qt.Orientation.Horizontal)
        self.jitter_x_slider.setMinimum(0)
        self.jitter_x_slider.setMaximum(3)
        self.jitter_x_slider.valueChanged.connect(self.select_jitter_x)
        self.grid_layout.addWidget(self.jitter_x_label, 1, 0)
        self.grid_layout.addWidget(self.jitter_x_slider, 1, 1)

        self.jitter_y_label = QLabel("Jitter Y:")
        self.jitter_y_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.jitter_y_slider = QSlider(Qt.Orientation.Horizontal)
        self.jitter_y_slider.setMinimum(0)
        self.jitter_y_slider.setMaximum(3)
        self.jitter_y_slider.valueChanged.connect(self.select_jitter_y)
        self.grid_layout.addWidget(self.jitter_y_label, 1, 2)
        self.grid_layout.addWidget(self.jitter_y_slider, 1, 3)

        self.point_size_label = QLabel("Size:")
        self.point_size_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.point_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.point_size_slider.setMinimum(0)
        self.point_size_slider.setMaximum(8)
        self.point_size_slider.valueChanged.connect(self.select_point_size)
        self.grid_layout.addWidget(self.point_size_label, 2, 0)
        self.grid_layout.addWidget(self.point_size_slider, 2, 1)

        self.grid_layout.setColumnStretch(1, 1)
        self.grid_layout.setColumnStretch(3, 1)
        self.grid_layout.setColumnMinimumWidth(0, 50)
        self.grid_layout.setColumnMinimumWidth(2, 50)

    def configure(self, scatter_plot_config: ScatterPlotConfig):
        self.scatter_plot_config = scatter_plot_config
        self.point_color_button_icon = qta.icon(
            "ei.stop", color=color_from_rgb_and_a(self.scatter_plot_config.color, 255)
        )
        self.point_color_button.setIcon(self.point_color_button_icon)
        self.fill_alpha_slider.setValue(self.scatter_plot_config.fill_alpha // 50)
        self.line_alpha_slider.setValue(self.scatter_plot_config.line_alpha // 50)
        self.point_size_slider.setValue(self.scatter_plot_config.point_size // 2)
        self.jitter_x_slider.setValue(int(self.scatter_plot_config.jitter_x * 3))
        self.jitter_y_slider.setValue(int(self.scatter_plot_config.jitter_y * 3))

    def select_color(self):
        color = QColorDialog.getColor(
            initial=color_from_rgb_and_a(self.scatter_plot_config.color, 255),
        )
        if color.isValid():
            self.scatter_plot_config.color = color.getRgb()[:3]
            self.handler(
                Message(MessageType.STATE_CHANGED, payload=self.scatter_plot_config, caller_id=self.element_id)
            )

    def select_fill_alpha(self, value):
        self.scatter_plot_config.fill_alpha = value * 50
        self.handler(Message(MessageType.STATE_CHANGED, payload=self.scatter_plot_config, caller_id=self.element_id))

    def select_line_alpha(self, value):
        self.scatter_plot_config.line_alpha = value * 50
        self.handler(Message(MessageType.STATE_CHANGED, payload=self.scatter_plot_config, caller_id=self.element_id))

    def select_marker(self, marker):
        self.scatter_plot_config.marker_shape = marker
        self.handler(Message(MessageType.STATE_CHANGED, payload=self.scatter_plot_config, caller_id=self.element_id))

    def select_point_size(self, value):
        self.scatter_plot_config.point_size = value * 2
        self.handler(Message(MessageType.STATE_CHANGED, payload=self.scatter_plot_config, caller_id=self.element_id))

    def select_jitter_x(self, value):
        self.scatter_plot_config.jitter_x = value / 3
        self.handler(Message(MessageType.STATE_CHANGED, payload=self.scatter_plot_config, caller_id=self.element_id))

    def select_jitter_y(self, value):
        self.scatter_plot_config.jitter_y = value / 3
        self.handler(Message(MessageType.STATE_CHANGED, payload=self.scatter_plot_config, caller_id=self.element_id))
