import qtawesome as qta
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QColorDialog, QComboBox, QPushButton, QSlider, QVBoxLayout, QWidget

from src.common.constant import PEN_STYLE_MAP
from src.common.elements.base.base import BasePanelElement
from src.common.messages import Message, MessageType
from src.common.result.classes.plot_result import LinePlotConfig


class LinePlotSettings(BasePanelElement):
    def setup(self):
        self.widget = QWidget(self.parent_widget)
        self.layout = QVBoxLayout(self.widget)

        self.line_color_button = QPushButton("Line Color")
        self.line_color_button.clicked.connect(self.select_color)
        self.layout.addWidget(self.line_color_button)

        self.line_style_selector = QComboBox()
        self.line_style_selector.addItems(list(PEN_STYLE_MAP.keys()))
        self.line_style_selector.currentTextChanged.connect(self.select_style)
        self.layout.addWidget(self.line_style_selector)

        self.line_width_slider = QSlider(Qt.Orientation.Horizontal)
        self.line_width_slider.setMinimum(0)
        self.line_width_slider.setMaximum(10)
        self.line_width_slider.valueChanged.connect(self.select_width)
        self.layout.addWidget(self.line_width_slider)

    def configure(self, line_plot_config: LinePlotConfig):
        self.line_plot_config = line_plot_config
        self.line_color_button_icon = qta.icon("ei.stop", color=self.line_plot_config.line_color)
        self.line_color_button.setIcon(self.line_color_button_icon)
        self.line_style_selector.setCurrentText(self.line_plot_config.line_style)
        self.line_width_slider.setValue(self.line_plot_config.line_width)

    def select_color(self):
        color = QColorDialog.getColor(
            initial=self.line_plot_config.line_color, options=QColorDialog.ColorDialogOption.ShowAlphaChannel
        )
        if color.isValid():
            self.line_plot_config.line_color = color
            self.handler(Message(MessageType.STATE_CHANGED, payload=self.line_plot_config, caller_id=self.element_id))

    def select_style(self, line_style):
        self.line_plot_config.line_style = line_style
        self.handler(Message(MessageType.STATE_CHANGED, payload=self.line_plot_config, caller_id=self.element_id))

    def select_width(self, value):
        self.line_plot_config.line_width = value
        self.handler(Message(MessageType.STATE_CHANGED, payload=self.line_plot_config, caller_id=self.element_id))
