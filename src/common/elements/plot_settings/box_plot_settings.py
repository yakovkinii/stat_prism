import qtawesome as qta
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QColorDialog, QGroupBox, QHBoxLayout, QLabel, QPushButton, QSlider, QVBoxLayout

from src.common.elements.base.base import BasePanelElement
from src.common.messages import Message, MessageType
from src.common.qcolor import color_from_rgb_and_a
from src.common.result.classes.plot_result import BoxPlotConfig


class BoxPlotSettings(BasePanelElement):
    def __init__(self, label_text):
        self.label_text = label_text
        super().__init__()

    def setup(self):
        self.widget = QGroupBox("Box", self.parent_widget)
        self.layout = QVBoxLayout(self.widget)

        self.top_layout = QHBoxLayout()
        self.layout.addLayout(self.top_layout)

        self.line_color_button = QPushButton("Color")
        self.line_color_button.clicked.connect(self.select_color)
        self.top_layout.addWidget(self.line_color_button)

        self.fill_alpha_layout = QHBoxLayout()
        self.fill_alpha_label = QLabel("Opacity:")
        self.fill_alpha_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.fill_alpha_slider = QSlider(Qt.Orientation.Horizontal)
        self.fill_alpha_slider.setMinimum(0)
        self.fill_alpha_slider.setMaximum(5)
        self.fill_alpha_slider.valueChanged.connect(self.select_fill_alpha)
        self.fill_alpha_layout.addWidget(self.fill_alpha_label)
        self.fill_alpha_layout.addWidget(self.fill_alpha_slider)
        self.top_layout.addLayout(self.fill_alpha_layout)

        self.top_layout.setStretch(0, 1)
        self.top_layout.setStretch(1, 1)

    def configure(self, box_plot_config: BoxPlotConfig):
        self.box_plot_config = box_plot_config
        self.bar_line_color_button_icon = qta.icon(
            "ei.stop", color=color_from_rgb_and_a(self.box_plot_config.color, 255)
        )
        self.line_color_button.setIcon(self.bar_line_color_button_icon)
        self.fill_alpha_slider.setValue(self.box_plot_config.fill_alpha // 50)

    def select_color(self):
        color = QColorDialog.getColor(initial=color_from_rgb_and_a(self.box_plot_config.color, 255))
        if color.isValid():
            self.box_plot_config.color = color.getRgb()[:3]
            self.handler(Message(MessageType.STATE_CHANGED, payload=self.box_plot_config, caller_id=self.element_id))

    def select_fill_alpha(self, value):
        self.box_plot_config.fill_alpha = value * 50
        self.handler(Message(MessageType.STATE_CHANGED, payload=self.box_plot_config, caller_id=self.element_id))
