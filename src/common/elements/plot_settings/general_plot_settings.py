import qtawesome as qta
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QColorDialog, QHBoxLayout, QLabel, QPushButton, QSlider, QVBoxLayout, QWidget

from src.common.elements.base.base import BasePanelElement
from src.common.messages import Message, MessageType
from src.common.qcolor import color_from_rgb_and_a
from src.common.result.classes.plot_result import GeneralPlotConfig
from src.common.unique_qss import set_stylesheet


class GeneralPlotSettings(BasePanelElement):
    def setup(self):
        self.widget = QWidget(self.parent_widget)
        self.layout = QVBoxLayout(self.widget)
        set_stylesheet(self.widget, "#id{border: 1px solid #ddd;}"),

        self.label = QLabel("General Settings:")
        self.layout.addWidget(self.label)

        self.background_color_button = QPushButton("Background color")
        self.background_color_button.clicked.connect(self.select_background_color)
        self.layout.addWidget(self.background_color_button)

        self.alpha_layout = QHBoxLayout()
        self.alpha_label = QLabel("Opacity:")
        self.alpha_label.setFixedWidth(70)
        self.alpha_slider = QSlider(Qt.Orientation.Horizontal)
        self.alpha_slider.setMinimum(0)
        self.alpha_slider.setMaximum(51)
        self.alpha_slider.valueChanged.connect(self.select_alpha)
        self.alpha_layout.addWidget(self.alpha_label)
        self.alpha_layout.addWidget(self.alpha_slider)
        self.layout.addLayout(self.alpha_layout)

    def configure(self, general_plot_config: GeneralPlotConfig):
        self.general_plot_config = general_plot_config
        self.background_color_button_icon = qta.icon(
            "ei.stop", color=color_from_rgb_and_a(self.general_plot_config.color, 255)
        )
        self.background_color_button.setIcon(self.background_color_button_icon)
        self.alpha_slider.setValue(self.general_plot_config.alpha // 5)

    def select_background_color(self):
        color = QColorDialog.getColor(
            initial=color_from_rgb_and_a(self.general_plot_config.color, 255),
        )
        if color.isValid():
            self.general_plot_config.color = color.getRgb()[:3]
            self.handler(
                Message(MessageType.STATE_CHANGED, payload=self.general_plot_config, caller_id=self.element_id)
            )

    def select_alpha(self, value):
        self.general_plot_config.alpha = value * 5
        self.handler(Message(MessageType.STATE_CHANGED, payload=self.general_plot_config, caller_id=self.element_id))
