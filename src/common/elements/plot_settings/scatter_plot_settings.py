import qtawesome as qta
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QColorDialog,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

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

        self.point_size_layout = QHBoxLayout()
        self.point_size_label = QLabel("Point Size")
        self.point_size_label.setFixedWidth(60)
        self.point_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.point_size_slider.setMinimum(0)
        self.point_size_slider.setMaximum(30)
        self.point_size_slider.valueChanged.connect(self.select_point_size)
        self.point_size_edit = QLineEdit()
        self.point_size_edit.setFixedWidth(50)
        self.point_size_edit.setText(str(self.point_size_slider.value()))
        self.point_size_edit.editingFinished.connect(self.update_point_size_slider)
        self.point_size_layout.addWidget(self.point_size_label)
        self.point_size_layout.addWidget(self.point_size_slider)
        self.point_size_layout.addWidget(self.point_size_edit)
        self.layout.addLayout(self.point_size_layout)

        self.jitter_x_layout = QHBoxLayout()
        self.jitter_x_label = QLabel("Jitter X")
        self.jitter_x_label.setFixedWidth(60)
        self.jitter_x_slider = QSlider(Qt.Orientation.Horizontal)
        self.jitter_x_slider.setMinimum(0)
        self.jitter_x_slider.setMaximum(10)
        self.jitter_x_slider.valueChanged.connect(self.select_jitter_x)
        self.jitter_x_edit = QLineEdit()
        self.jitter_x_edit.setFixedWidth(50)
        self.jitter_x_edit.setText(str(self.jitter_x_slider.value() / 10))
        self.jitter_x_edit.editingFinished.connect(self.update_jitter_x_slider)
        self.jitter_x_layout.addWidget(self.jitter_x_label)
        self.jitter_x_layout.addWidget(self.jitter_x_slider)
        self.jitter_x_layout.addWidget(self.jitter_x_edit)
        self.layout.addLayout(self.jitter_x_layout)

        self.jitter_y_layout = QHBoxLayout()
        self.jitter_y_label = QLabel("Jitter Y")
        self.jitter_y_label.setFixedWidth(60)
        self.jitter_y_slider = QSlider(Qt.Orientation.Horizontal)
        self.jitter_y_slider.setMinimum(0)
        self.jitter_y_slider.setMaximum(10)
        self.jitter_y_slider.valueChanged.connect(self.select_jitter_y)
        self.jitter_y_edit = QLineEdit()
        self.jitter_y_edit.setFixedWidth(50)
        self.jitter_y_edit.setText(str(self.jitter_y_slider.value() / 10))
        self.jitter_y_edit.editingFinished.connect(self.update_jitter_y_slider)
        self.jitter_y_layout.addWidget(self.jitter_y_label)
        self.jitter_y_layout.addWidget(self.jitter_y_slider)
        self.jitter_y_layout.addWidget(self.jitter_y_edit)
        self.layout.addLayout(self.jitter_y_layout)

    def configure(self, scatter_plot_config: ScatterPlotConfig):
        self.scatter_plot_config = scatter_plot_config
        self.point_color_button_icon = qta.icon("ei.stop", color=self.scatter_plot_config.point_color)
        self.point_color_button.setIcon(self.point_color_button_icon)
        self.outline_color_button_icon = qta.icon("ei.stop", color=self.scatter_plot_config.outline_color)
        self.outline_color_button.setIcon(self.outline_color_button_icon)
        self.point_size_slider.setValue(self.scatter_plot_config.point_size)
        self.point_size_edit.setText(str(self.scatter_plot_config.point_size))
        self.jitter_x_slider.setValue(int(self.scatter_plot_config.jitter_x * 10))
        self.jitter_x_edit.setText(str(self.scatter_plot_config.jitter_x))
        self.jitter_y_slider.setValue(int(self.scatter_plot_config.jitter_y * 10))
        self.jitter_y_edit.setText(str(self.scatter_plot_config.jitter_y))

    def select_color(self):
        color = QColorDialog.getColor(
            initial=self.scatter_plot_config.point_color, options=QColorDialog.ColorDialogOption.ShowAlphaChannel
        )
        if color.isValid():
            self.scatter_plot_config.point_color = color
            self.handler(
                Message(MessageType.STATE_CHANGED, payload=self.scatter_plot_config, caller_id=self.element_id)
            )

    def select_outline_color(self):
        color = QColorDialog.getColor(
            initial=self.scatter_plot_config.outline_color, options=QColorDialog.ColorDialogOption.ShowAlphaChannel
        )
        if color.isValid():
            self.scatter_plot_config.outline_color = color
            self.handler(
                Message(MessageType.STATE_CHANGED, payload=self.scatter_plot_config, caller_id=self.element_id)
            )

    def select_marker(self, marker):
        self.scatter_plot_config.marker_shape = marker
        self.handler(Message(MessageType.STATE_CHANGED, payload=self.scatter_plot_config, caller_id=self.element_id))

    def select_point_size(self, value):
        self.scatter_plot_config.point_size = value
        self.point_size_edit.setText(str(value))
        self.handler(Message(MessageType.STATE_CHANGED, payload=self.scatter_plot_config, caller_id=self.element_id))

    def select_jitter_x(self, value):
        self.scatter_plot_config.jitter_x = value / 10
        self.jitter_x_edit.setText(str(value / 10))
        self.handler(Message(MessageType.STATE_CHANGED, payload=self.scatter_plot_config, caller_id=self.element_id))

    def select_jitter_y(self, value):
        self.scatter_plot_config.jitter_y = value / 10
        self.jitter_y_edit.setText(str(value / 10))
        self.handler(Message(MessageType.STATE_CHANGED, payload=self.scatter_plot_config, caller_id=self.element_id))

    def update_point_size_slider(self):
        value = int(self.point_size_edit.text())
        self.point_size_slider.setValue(value)

    def update_jitter_x_slider(self):
        value = float(self.jitter_x_edit.text()) * 10
        self.jitter_x_slider.setValue(int(value))

    def update_jitter_y_slider(self):
        value = float(self.jitter_y_edit.text()) * 10
        self.jitter_y_slider.setValue(int(value))
