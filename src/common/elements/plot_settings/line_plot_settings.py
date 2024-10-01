import qtawesome as qta
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QColorDialog, QComboBox, QHBoxLayout, QLabel, QPushButton, QSlider, QVBoxLayout, QWidget

from src.common.constant import PEN_STYLE_MAP
from src.common.elements.base.base import BasePanelElement
from src.common.messages import Message, MessageType
from src.common.qcolor import color_from_rgb_and_a
from src.common.result.classes.plot_result import LinePlotConfig
from src.common.unique_qss import set_stylesheet


class LinePlotSettings(BasePanelElement):
    def __init__(self, label_text):
        self.label_text = label_text
        super().__init__()

    def setup(self):
        self.widget = QWidget(self.parent_widget)
        self.layout = QVBoxLayout(self.widget)
        set_stylesheet(self.widget, "#id{border: 1px solid #ddd;}"),

        self.label = QLabel("Line Settings:")
        self.layout.addWidget(self.label)

        self.line_color_button = QPushButton("Line Color")
        self.line_color_button.clicked.connect(self.select_color)
        self.layout.addWidget(self.line_color_button)

        self.line_alpha_layout = QHBoxLayout()
        self.line_alpha_label = QLabel("Line Opacity:")
        self.line_alpha_label.setFixedWidth(70)
        self.line_alpha_slider = QSlider(Qt.Orientation.Horizontal)
        self.line_alpha_slider.setMinimum(0)
        self.line_alpha_slider.setMaximum(51)
        self.line_alpha_slider.valueChanged.connect(self.select_line_alpha)
        self.line_alpha_layout.addWidget(self.line_alpha_label)
        self.line_alpha_layout.addWidget(self.line_alpha_slider)
        self.layout.addLayout(self.line_alpha_layout)

        self.line_style_selector = QComboBox()
        self.line_style_selector.addItems(list(PEN_STYLE_MAP.keys()))
        self.line_style_selector.currentTextChanged.connect(self.select_style)
        self.layout.addWidget(self.line_style_selector)

        self.line_width_layout = QHBoxLayout()
        self.line_width_label = QLabel("Line Width:")
        self.line_width_label.setFixedWidth(70)
        self.line_width_slider = QSlider(Qt.Orientation.Horizontal)
        self.line_width_slider.setMinimum(0)
        self.line_width_slider.setMaximum(10)
        self.line_width_slider.valueChanged.connect(self.select_width)
        self.line_width_layout.addWidget(self.line_width_label)
        self.line_width_layout.addWidget(self.line_width_slider)
        self.layout.addLayout(self.line_width_layout)

    def configure(self, line_plot_config: LinePlotConfig):
        self.line_plot_config = line_plot_config
        self.label.setText(f"Line Settings ({self.label_text}):")
        self.line_color_button_icon = qta.icon("ei.stop", color=color_from_rgb_and_a(self.line_plot_config.color, 255))
        self.line_color_button.setIcon(self.line_color_button_icon)
        self.line_alpha_slider.setValue(self.line_plot_config.line_alpha // 5)
        self.line_style_selector.setCurrentText(self.line_plot_config.line_style)
        self.line_width_slider.setValue(self.line_plot_config.line_width)

    def select_color(self):
        color = QColorDialog.getColor(initial=color_from_rgb_and_a(self.line_plot_config.color, 255))
        if color.isValid():
            self.line_plot_config.color = color.getRgb()[:3]
            self.handler(Message(MessageType.STATE_CHANGED, payload=self.line_plot_config, caller_id=self.element_id))

    def select_line_alpha(self, value):
        self.line_plot_config.line_alpha = value * 5
        self.handler(Message(MessageType.STATE_CHANGED, payload=self.line_plot_config, caller_id=self.element_id))

    def select_style(self, line_style):
        self.line_plot_config.line_style = line_style
        self.handler(Message(MessageType.STATE_CHANGED, payload=self.line_plot_config, caller_id=self.element_id))

    def select_width(self, value):
        self.line_plot_config.line_width = value
        self.handler(Message(MessageType.STATE_CHANGED, payload=self.line_plot_config, caller_id=self.element_id))
