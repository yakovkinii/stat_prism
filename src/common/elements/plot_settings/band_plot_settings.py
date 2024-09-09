import qtawesome as qta
from PySide6.QtWidgets import QColorDialog, QPushButton, QVBoxLayout, QWidget

from src.common.elements.base.base import BasePanelElement
from src.common.messages import Message, MessageType
from src.common.result.classes.plot_result import BandPlotConfig


class BandPlotSettings(BasePanelElement):
    def setup(self):
        self.widget = QWidget(self.parent_widget)
        self.layout = QVBoxLayout(self.widget)

        self.line_color_button = QPushButton("Line color")
        self.line_color_button.clicked.connect(self.select_color)
        self.layout.addWidget(self.line_color_button)

        self.fill_color_button = QPushButton("Fill color")
        self.fill_color_button.clicked.connect(self.select_fill_color)
        self.layout.addWidget(self.fill_color_button)

    def configure(self, band_plot_config: BandPlotConfig):
        self.band_plot_config = band_plot_config

        self.line_color_button_icon = qta.icon("ei.stop", color=self.band_plot_config.line_color)
        self.line_color_button.setIcon(self.line_color_button_icon)

        self.fill_color_button_icon = qta.icon("ei.stop", color=self.band_plot_config.fill_color)
        self.fill_color_button.setIcon(self.fill_color_button_icon)

    def select_color(self):
        color = QColorDialog.getColor(
            initial=self.band_plot_config.line_color, options=QColorDialog.ColorDialogOption.ShowAlphaChannel
        )
        if color.isValid():
            self.band_plot_config.line_color = color
            self.handler(Message(MessageType.STATE_CHANGED, payload=self.band_plot_config, caller_id=self.element_id))

    def select_fill_color(self):
        color = QColorDialog.getColor(
            initial=self.band_plot_config.fill_color, options=QColorDialog.ColorDialogOption.ShowAlphaChannel
        )
        if color.isValid():
            self.band_plot_config.fill_color = color
            self.handler(Message(MessageType.STATE_CHANGED, payload=self.band_plot_config, caller_id=self.element_id))
