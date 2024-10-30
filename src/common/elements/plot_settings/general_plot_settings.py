import qtawesome as qta
from PySide6.QtWidgets import QCheckBox, QColorDialog, QGridLayout, QGroupBox, QPushButton

from src.common.elements.base.base import BasePanelElement
from src.common.messages import Message, MessageType
from src.common.qcolor import color_from_rgb_and_a
from src.common.result.classes.plot_result import GeneralPlotConfig


class GeneralPlotSettings(BasePanelElement):
    def setup(self):
        self.widget = QGroupBox("General", self.parent_widget)
        self.layout = QGridLayout(self.widget)

        self.background_color_button = QPushButton("Background")
        self.background_color_button.clicked.connect(self.select_background_color)
        self.layout.addWidget(self.background_color_button, 0, 0)

        self.transparent_checkbox = QCheckBox("Transparent")
        self.transparent_checkbox.setEnabled(False)
        self.transparent_checkbox.stateChanged.connect(self.transparent)
        self.layout.addWidget(self.transparent_checkbox, 0, 1)

        self.tilt_checkbox = QCheckBox("Tilt x-axis labels")
        self.tilt_checkbox.stateChanged.connect(self.tilt_x_axis_labels)
        self.layout.addWidget(self.tilt_checkbox, 1, 0)

    def configure(self, general_plot_config: GeneralPlotConfig):
        self.general_plot_config = general_plot_config
        self.background_color_button_icon = qta.icon(
            "ei.stop", color=color_from_rgb_and_a(self.general_plot_config.color, 255)
        )
        self.background_color_button.setIcon(self.background_color_button_icon)
        self.transparent_checkbox.setChecked(self.general_plot_config.transparent)
        self.tilt_checkbox.setChecked(self.general_plot_config.tilt_x_axis_labels)

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

    def tilt_x_axis_labels(self, state):
        self.general_plot_config.tilt_x_axis_labels = state
        self.handler(Message(MessageType.STATE_CHANGED, payload=self.general_plot_config, caller_id=self.element_id))

    def transparent(self, state):
        self.general_plot_config.transparent = state
        self.handler(Message(MessageType.STATE_CHANGED, payload=self.general_plot_config, caller_id=self.element_id))
