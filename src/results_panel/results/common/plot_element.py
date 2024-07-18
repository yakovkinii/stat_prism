from typing import List, Union

import pyqtgraph as pg
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from src.results_panel.results.common.base import BaseResultElement


class Scatter:
    def __init__(self, x, y, label=None):
        self.x = x
        self.y = y
        self.label = label


class PlotResultElement(BaseResultElement):
    def __init__(
        self,
        tab_title="Plot Result Element",
        plot_id="1",
        plot_title="Correlation plot",
        x_axis_title="",
        y_axis_title="",
    ):
        super().__init__()
        self.title: str = tab_title
        self.class_id: str = "PlotResultElement"
        self.items: List[Union[Scatter]] = []
        self.plot_id = plot_id
        self.plot_title = plot_title
        self.x_axis_title = x_axis_title
        self.y_axis_title = y_axis_title


class PlotResultElementWidgetContainer:
    def __init__(self, parent_widget, result_element: PlotResultElement):
        self.result_element = result_element
        self.widget = QWidget(parent_widget)
        self.widget_layout = QVBoxLayout(self.widget)
        self.widget_layout.setContentsMargins(20, 20, 20, 20)

        self.label = QLabel(self.widget)
        self.label.setText(
            f"""
            <span><b> Figure {self.result_element.plot_id} </b> </span> <br><br>
            <span><i> {self.result_element.plot_title} </i> </span> <br><br>
            """
        )

        self.widget_layout.addWidget(self.label)

        self.plot_widget = pg.PlotWidget(self.widget)
        self.plot_widget.plotItem.setDefaultPadding(0.2)
        self.plot_widget.setFixedWidth(600)
        self.plot_widget.setFixedHeight(600)
        self.widget_layout.addWidget(self.plot_widget)
        self.widget_layout.addStretch()

        self.items = []
        for item in self.result_element.items:
            if isinstance(item, Scatter):
                plot_item = pg.ScatterPlotItem(item.x, item.y, pen=None, symbol="o", brush="b")
                self.plot_widget.addItem(plot_item)
        self.customize_plot()

    def customize_plot(self):
        # Get the plot item
        plot_item = self.plot_widget.getPlotItem()

        # Customize the axes
        plot_item.getAxis("left").setPen(pg.mkPen(color="black", width=2))
        plot_item.getAxis("bottom").setPen(pg.mkPen(color="black", width=2))

        # Customize the font of axis labels and tick marks
        axis_font = pg.Qt.QtGui.QFont()
        axis_font.setPointSize(14)  # Set the font size for axis labels and tick marks
        plot_item.getAxis("left").setTickFont(axis_font)
        plot_item.getAxis("bottom").setTickFont(axis_font)

        # Customize the labels themselves
        plot_item.getAxis("left").setLabel(self.result_element.y_axis_title, **{"font-size": "14pt"})
        plot_item.getAxis("bottom").setLabel(self.result_element.x_axis_title, **{"font-size": "14pt"})

        # Optional: Set the background to white for better contrast
        self.plot_widget.setBackground("w")
