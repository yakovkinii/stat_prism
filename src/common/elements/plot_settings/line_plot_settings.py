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

from src.common.constant import PEN_STYLE_MAP
from src.common.elements.base.base import BasePanelElement
from src.common.messages import Message, MessageType
from src.common.qcolor import color_from_rgb_and_a
from src.common.result.classes.plot_result import LinePlotConfig


class LinePlotSettings(BasePanelElement):
    def __init__(self, label_text):
        self.label_text = label_text
        super().__init__()

    def setup(self):
        self.widget = QGroupBox("Line", self.parent_widget)
        self.layout = QVBoxLayout(self.widget)

        self.top_layout = QHBoxLayout()
        self.layout.addLayout(self.top_layout)

        self.line_color_button = QPushButton("Color")
        self.line_color_button.clicked.connect(self.select_color)
        self.top_layout.addWidget(self.line_color_button)

        self.line_style_selector = QComboBox()
        self.line_style_selector.addItems(list(PEN_STYLE_MAP.keys()))
        self.line_style_selector.currentTextChanged.connect(self.select_style)
        self.top_layout.addWidget(self.line_style_selector)

        self.grid_layout = QGridLayout()
        self.layout.addLayout(self.grid_layout)

        self.line_alpha_label = QLabel("Opacity:")
        self.line_alpha_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.grid_layout.addWidget(self.line_alpha_label, 0, 0)

        self.line_alpha_slider = QSlider(Qt.Orientation.Horizontal)
        self.line_alpha_slider.setMinimum(0)
        self.line_alpha_slider.setMaximum(5)
        self.line_alpha_slider.valueChanged.connect(self.select_line_alpha)
        self.grid_layout.addWidget(self.line_alpha_slider, 0, 1)

        self.line_width_label = QLabel("Width:")
        self.line_width_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.grid_layout.addWidget(self.line_width_label, 0, 2)

        self.line_width_slider = QSlider(Qt.Orientation.Horizontal)
        self.line_width_slider.setMinimum(2)
        self.line_width_slider.setMaximum(6)
        self.line_width_slider.valueChanged.connect(self.select_width)
        self.grid_layout.addWidget(self.line_width_slider, 0, 3)

        self.grid_layout.setColumnStretch(1, 1)
        self.grid_layout.setColumnStretch(3, 1)
        self.grid_layout.setColumnMinimumWidth(0, 50)
        self.grid_layout.setColumnMinimumWidth(2, 50)

    def configure(self, line_plot_config: LinePlotConfig):
        self.line_plot_config = line_plot_config
        self.line_color_button_icon = qta.icon("ei.stop", color=color_from_rgb_and_a(self.line_plot_config.color, 255))
        self.line_color_button.setIcon(self.line_color_button_icon)
        self.line_alpha_slider.setValue(self.line_plot_config.line_alpha // 50)
        self.line_style_selector.setCurrentText(self.line_plot_config.line_style)
        self.line_width_slider.setValue(self.line_plot_config.line_width)

    def select_color(self):
        color = QColorDialog.getColor(initial=color_from_rgb_and_a(self.line_plot_config.color, 255))
        if color.isValid():
            self.line_plot_config.color = color.getRgb()[:3]
            self.handler(Message(MessageType.STATE_CHANGED, payload=self.line_plot_config, caller_id=self.element_id))

    def select_line_alpha(self, value):
        self.line_plot_config.line_alpha = value * 50
        self.handler(Message(MessageType.STATE_CHANGED, payload=self.line_plot_config, caller_id=self.element_id))

    def select_style(self, line_style):
        self.line_plot_config.line_style = line_style
        self.handler(Message(MessageType.STATE_CHANGED, payload=self.line_plot_config, caller_id=self.element_id))

    def select_width(self, value):
        self.line_plot_config.line_width = value
        self.handler(Message(MessageType.STATE_CHANGED, payload=self.line_plot_config, caller_id=self.element_id))
