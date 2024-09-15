import qtawesome as qta
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QColorDialog, QPushButton, QVBoxLayout, QWidget

from src.common.elements.base.base import BasePanelElement
from src.common.messages import Message, MessageType
from src.common.result.classes.plot_result import GeneralPlotConfig


class GeneralPlotSettings(BasePanelElement):
    def setup(self):
        self.widget = QWidget(self.parent_widget)
        self.layout = QVBoxLayout(self.widget)

        self.background_color_button = QPushButton("Background color")
        self.background_color_button.clicked.connect(self.select_background_color)
        self.layout.addWidget(self.background_color_button)

    def configure(self, general_plot_config: GeneralPlotConfig):
        self.general_plot_config = general_plot_config
        self.background_color_button_icon = qta.icon("ei.stop", color=self.general_plot_config.background_color)
        self.background_color_button.setIcon(self.background_color_button_icon)

    def select_background_color(self):
        color = QColorDialog.getColor(
            initial=QColor(self.general_plot_config.background_color),
            options=QColorDialog.ColorDialogOption.ShowAlphaChannel,
        )
        if color.isValid():
            self.general_plot_config.background_color = color
            self.handler(
                Message(MessageType.STATE_CHANGED, payload=self.general_plot_config, caller_id=self.element_id)
            )
