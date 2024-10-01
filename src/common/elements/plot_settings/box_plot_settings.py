import qtawesome as qta
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QColorDialog, QHBoxLayout, QLabel, QPushButton, QSlider, QVBoxLayout, QWidget

from src.common.elements.base.base import BasePanelElement
from src.common.messages import Message, MessageType
from src.common.qcolor import color_from_rgb_and_a
from src.common.result.classes.plot_result import BoxPlotConfig
from src.common.unique_qss import set_stylesheet


class BoxPlotSettings(BasePanelElement):
    def __init__(self, label_text):
        self.label_text = label_text
        super().__init__()

    def setup(self):
        self.widget = QWidget(self.parent_widget)
        self.layout = QVBoxLayout(self.widget)
        set_stylesheet(self.widget, "#id{border: 1px solid #ddd;}"),

        self.label = QLabel("Box Settings:")
        self.layout.addWidget(self.label)

        self.line_color_button = QPushButton("Color")
        self.line_color_button.clicked.connect(self.select_line_color)
        self.layout.addWidget(self.line_color_button)

        self.fill_alpha_layout = QHBoxLayout()
        self.fill_alpha_label = QLabel("Fill Opacity:")
        self.fill_alpha_label.setFixedWidth(70)
        self.fill_alpha_slider = QSlider(Qt.Orientation.Horizontal)
        self.fill_alpha_slider.setMinimum(0)
        self.fill_alpha_slider.setMaximum(51)
        self.fill_alpha_slider.valueChanged.connect(self.select_fill_alpha)
        self.fill_alpha_layout.addWidget(self.fill_alpha_label)
        self.fill_alpha_layout.addWidget(self.fill_alpha_slider)
        self.layout.addLayout(self.fill_alpha_layout)

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

    def configure(self, box_plot_config: BoxPlotConfig):
        self.box_plot_config = box_plot_config
        self.label.setText(f"Box Settings ({self.label_text}):")
        self.bar_line_color_button_icon = qta.icon(
            "ei.stop", color=color_from_rgb_and_a(self.box_plot_config.color, 255)
        )
        self.line_color_button.setIcon(self.bar_line_color_button_icon)
        self.fill_alpha_slider.setValue(self.box_plot_config.fill_alpha // 5)
        self.line_alpha_slider.setValue(self.box_plot_config.line_alpha // 5)

    def select_line_color(self):
        color = QColorDialog.getColor(
            initial=color_from_rgb_and_a(self.box_plot_config.color, 255),
        )
        if color.isValid():
            self.box_plot_config.color = color.getRgb()[:3]
            self.handler(Message(MessageType.STATE_CHANGED, payload=self.box_plot_config, caller_id=self.element_id))

    def select_fill_alpha(self, value):
        self.box_plot_config.fill_alpha = value * 5
        self.handler(Message(MessageType.STATE_CHANGED, payload=self.box_plot_config, caller_id=self.element_id))

    def select_line_alpha(self, value):
        self.box_plot_config.line_alpha = value * 5
        self.handler(Message(MessageType.STATE_CHANGED, payload=self.box_plot_config, caller_id=self.element_id))
