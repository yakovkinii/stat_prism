#
#  Copyright (c) 2023 -- 2024 StatPrism Team. All rights reserved.
#

import os

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QFont, QImage
from PySide6.QtWidgets import QApplication, QLabel, QMenu, QSizePolicy, QVBoxLayout, QWidget

from src.common.elements.utility.layout_helpers import empty_widget
from src.common.result.classes.plot_result import PlotResultElement


class PlotResultElementWidgetContainer:
    def __init__(self, parent_widget, result_element: PlotResultElement):
        self.result_element = result_element
        self.widget, self.widget_layout = empty_widget(
            parent=parent_widget,
            inner_layout_class=QVBoxLayout,
            setup=lambda widget, layout: [
                layout.setContentsMargins(20, 20, 20, 20),
                layout.setSpacing(20),
            ],
        )

        self.label = QLabel(self.widget)
        self.label.setText(
            f"""
            <div><b> Figure {self.result_element.plot_id} </b> </div>
            <div><i> {self.result_element.plot_title} </i> </div>
            """
        )
        font = QFont(
            "Times New Roman",
            12,
        )
        self.label.setFont(font)
        self.label.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.label.setWordWrap(True)
        self.label.setTextInteractionFlags(
            self.label.textInteractionFlags() | Qt.TextInteractionFlag.TextSelectableByMouse
        )

        self.widget_layout.addWidget(self.label)

        self.plot_container = QWidget(self.widget)
        self.plot_container.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding))

        self.widget_layout.addWidget(self.plot_container)

        self.canvas = MatplotlibCanvas(parent=self.plot_container, result_element=self.result_element)
        # self.canvas.setFixedSize(
        #     self.result_element.general_plot_config.size_x, self.result_element.general_plot_config.size_y
        # )

        self.plot_container.setLayout(QVBoxLayout())
        self.plot_container.layout().addWidget(self.canvas)
        self.plot_container.layout().addStretch()


class MatplotlibCanvas(FigureCanvas):
    def __init__(self, parent, result_element: PlotResultElement):
        self.result_element = result_element
        self.fig, self.ax = self.result_element.create_figure()
        super().__init__(self.fig)
        self.setParent(parent)
        # Set initial state for dragging and zooming
        self.is_dragging = False
        self.dragged_after_click = False
        self.is_zooming = False
        self.last_mouse_position = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.dragged_after_click = False
            self.last_mouse_position = event.pos()
        elif event.button() == Qt.MouseButton.RightButton:
            self.is_zooming = True
            self.dragged_after_click = False
            self.last_mouse_position = event.pos()

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            self.dragged_after_click = True
            # Calculate the distance moved in mouse coordinates
            delta = event.pos() - self.last_mouse_position
            self.last_mouse_position = event.pos()

            # Calculate range adjustment factor
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()

            # Translate axis based on mouse movement for dragging
            dx = (xlim[1] - xlim[0]) * delta.x() / self.width()
            dy = (ylim[1] - ylim[0]) * delta.y() / self.height()

            # Update axis limits for panning effect
            self.ax.set_xlim(xlim[0] - dx, xlim[1] - dx)
            self.ax.set_ylim(ylim[0] + dy, ylim[1] + dy)

            # self.result_element.general_plot_config.x_range = self.ax.get_xlim()
            # self.result_element.general_plot_config.y_range = self.ax.get_ylim()

            self.draw()

        elif self.is_zooming:
            self.dragged_after_click = True
            # Calculate zoom factor based on vertical mouse movement
            delta = event.pos() - self.last_mouse_position
            self.last_mouse_position = event.pos()

            # Get current axis limits
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()

            # Calculate zoom scale (positive for zoom in, negative for zoom out)

            zoom_scale_x = delta.x() / self.width()
            zoom_scale_y = delta.y() / self.height()

            # Apply zoom scale to x and y ranges
            x_range = (xlim[1] - xlim[0]) * (1 - zoom_scale_x)
            y_range = (ylim[1] - ylim[0]) * (1 + zoom_scale_y)

            # Calculate new limits, centering on the middle of the current view
            x_mid = (xlim[0] + xlim[1]) / 2
            y_mid = (ylim[0] + ylim[1]) / 2

            new_xlim = [x_mid - x_range / 2, x_mid + x_range / 2]
            new_ylim = [y_mid - y_range / 2, y_mid + y_range / 2]

            # Set the new limits
            self.ax.set_xlim(new_xlim)
            self.ax.set_ylim(new_ylim)

            # self.result_element.general_plot_config.x_range = self.ax.get_xlim()
            # self.result_element.general_plot_config.y_range = self.ax.get_ylim()

            self.draw()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
        elif event.button() == Qt.MouseButton.RightButton:
            self.is_zooming = False

    def contextMenuEvent(self, event):
        if self.dragged_after_click:
            event.accept()
            return
        context_menu = QMenu(self)
        copy_action = QAction("Copy", self)
        copy_action.triggered.connect(self.copy_as_image_to_clipboard)
        context_menu.addAction(copy_action)
        context_menu.exec(event.globalPos())
        event.accept()

    def copy_as_image_to_clipboard(self):
        temp_file_name = "./~tmp.png"
        self.fig.savefig(temp_file_name, format="png", bbox_inches="tight", dpi=300)

        image = QImage()
        image.load(temp_file_name)

        clipboard = QApplication.clipboard()
        clipboard.setImage(image)

        os.remove(temp_file_name)
