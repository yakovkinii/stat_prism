import qtawesome as qta
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QColorDialog, QComboBox, QPushButton, QSlider, QVBoxLayout, QWidget

from src.common.constant import MARKER_SHAPE_MAP
from src.common.elements.base.base import BasePanelElement
from src.common.messages import Message, MessageType
from src.common.result.classes.plot_result import ScatterPlotConfig


class ScatterPlotSettings(BasePanelElement):
    def setup(self):
        self.widget = QWidget(self.parent_widget)
        self.layout = QVBoxLayout(self.widget)

        self.point_color_button = QPushButton("Fill color")
        self.point_color_button.clicked.connect(self.select_color)
        self.layout.addWidget(self.point_color_button)

        self.outline_color_button = QPushButton("Outline color")
        self.outline_color_button.clicked.connect(self.select_outline_color)
        self.layout.addWidget(self.outline_color_button)

        self.marker_shape_selector = QComboBox()
        self.marker_shape_selector.addItems(list(MARKER_SHAPE_MAP.keys()))
        self.marker_shape_selector.currentTextChanged.connect(self.select_marker)
        self.layout.addWidget(self.marker_shape_selector)

        self.point_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.point_size_slider.setMinimum(0)
        self.point_size_slider.setMaximum(30)
        self.point_size_slider.valueChanged.connect(self.select_point_size)
        self.layout.addWidget(self.point_size_slider)

    def configure(self, scatter_plot_config: ScatterPlotConfig):
        self.scatter_plot_config = scatter_plot_config
        self.point_color_button_icon = qta.icon("ei.stop", color=self.scatter_plot_config.point_color)
        self.point_color_button.setIcon(self.point_color_button_icon)
        self.outline_color_button_icon = qta.icon("ei.stop", color=self.scatter_plot_config.outline_color)
        self.outline_color_button.setIcon(self.outline_color_button_icon)
        self.point_size_slider.setValue(self.scatter_plot_config.point_size)

    def select_color(self):
        color = QColorDialog.getColor(
            initial=self.scatter_plot_config.point_color, options=QColorDialog.ColorDialogOption.ShowAlphaChannel
        )
        if color.isValid():
            self.scatter_plot_config.point_color = color
            print(self.scatter_plot_config.point_color)
            self.handler(
                Message(MessageType.STATE_CHANGED, payload=self.scatter_plot_config, caller_id=self.element_id)
            )

    def select_outline_color(self):
        color = QColorDialog.getColor(
            initial=self.scatter_plot_config.outline_color, options=QColorDialog.ColorDialogOption.ShowAlphaChannel
        )
        if color.isValid():
            self.scatter_plot_config.outline_color = color
            print(self.scatter_plot_config.outline_color)
            self.handler(
                Message(MessageType.STATE_CHANGED, payload=self.scatter_plot_config, caller_id=self.element_id)
            )

    def select_marker(self, marker):
        self.scatter_plot_config.marker_shape = marker
        self.handler(Message(MessageType.STATE_CHANGED, payload=self.scatter_plot_config, caller_id=self.element_id))

    def select_point_size(self, value):
        self.scatter_plot_config.point_size = value
        self.handler(Message(MessageType.STATE_CHANGED, payload=self.scatter_plot_config, caller_id=self.element_id))
