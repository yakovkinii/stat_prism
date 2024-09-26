import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget

from src.common.constant import MARKER_SHAPE_MAP, PEN_STYLE_MAP
from src.common.elements.resizeable_plot_widget.resizeable_plot_widget import ResizablePlotWidget
from src.common.elements.utility.layout_helpers import empty_widget
from src.common.result.classes.plot_result import Band, Bar, Line, PlotResultElement, Scatter
from src.common.unique_qss import set_stylesheet


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

        self.plot_container_class = PlotResultElementWidgetContainerExport(
            parent_widget=self.plot_container, result_element=self.result_element
        )


class PlotResultElementWidgetContainerExport:
    def __init__(self, parent_widget, result_element: PlotResultElement):
        self.result_element = result_element

        self.plot_widget = ResizablePlotWidget(parent_widget, self.result_element)
        legend = None

        self.restore_axis_ranges()

        self.plot_widget.plotItem.vb.sigRangeChanged.connect(self.on_range_changed)

        set_stylesheet(self.plot_widget, f"#id{{border: 2px solid #ccc;}}")

        self.plot_widget.setBackground(self.result_element.general_plot_config.background_color)

        self.plot_widget.plotItem.setDefaultPadding(0.1)

        self.plot_widget.plotItem.layout.setContentsMargins(20, 20, 20, 20)

        self.items = []
        for item in self.result_element.items:
            if isinstance(item, Scatter):
                np.random.seed(0)

                if item.scatter_plot_config.jitter_x == 0:
                    x_data = item.x
                else:
                    amplitude = (item.x.max() - item.x.min()) * 0.1
                    if amplitude == 0:
                        amplitude = item.x.max() * 0.1
                    x_data = (
                        item.x + item.scatter_plot_config.jitter_x * (np.random.rand(len(item.x)) - 0.5) * amplitude
                    )

                if item.scatter_plot_config.jitter_y == 0:
                    y_data = item.y
                else:
                    amplitude = (item.y.max() - item.y.min()) * 0.1
                    if amplitude == 0:
                        amplitude = item.y.max() * 0.1
                    y_data = (
                        item.y + item.scatter_plot_config.jitter_y * (np.random.rand(len(item.y)) - 0.5) * amplitude
                    )

                plot_item = pg.ScatterPlotItem(x_data, y_data, pen=None, symbol="o", brush="b")
                self.plot_widget.addItem(plot_item)

                plot_item.setBrush(pg.mkBrush(item.scatter_plot_config.point_color))
                plot_item.setPen(pg.mkPen(item.scatter_plot_config.outline_color))
                plot_item.setSymbol(MARKER_SHAPE_MAP[item.scatter_plot_config.marker_shape])
                plot_item.setSize(item.scatter_plot_config.point_size)

            if isinstance(item, Line):
                plot_item = self.plot_widget.plot(item.x, item.y)
                if item.legend_string != "":
                    if legend is None:
                        legend = pg.LegendItem()  # Create a LegendItem object
                        legend.setParentItem(self.plot_widget.plotItem)
                        legend.anchor((1, 0), (1, 0))
                    legend.addItem(plot_item, item.legend_string)
                plot_item.setBrush(pg.mkBrush(item.line_plot_config.line_color))
                plot_item.setPen(
                    pg.mkPen(
                        item.line_plot_config.line_color,
                        width=item.line_plot_config.line_width,
                        style=PEN_STYLE_MAP[item.line_plot_config.line_style],
                    )
                )

            if isinstance(item, Bar):
                plot_item = pg.BarGraphItem(
                    x=item.x,
                    height=item.y,
                    width=item.width,
                    brush=pg.mkBrush(item.bar_plot_config.fill_color),
                    pen=pg.mkPen(item.bar_plot_config.line_color),
                )
                self.plot_widget.addItem(plot_item)

            if isinstance(item, Band):
                curve1 = pg.PlotCurveItem(item.x, item.y1, pen=item.band_plot_config.line_color)
                curve2 = pg.PlotCurveItem(item.x, item.y2, pen=item.band_plot_config.line_color)
                fill = pg.FillBetweenItem(curve1, curve2, brush=item.band_plot_config.fill_color)
                self.plot_widget.addItem(curve1)
                self.plot_widget.addItem(curve2)
                self.plot_widget.addItem(fill)
                # plot_item.setBrush(pg.mkBrush(item.band_plot_config.fill_color))
                # plot_item.setPen(pg.mkPen(item.band_plot_config.line_color))

        # Get the plot item
        plot_item = self.plot_widget.getPlotItem()
        plot_item.setMenuEnabled(False)

        # Customize the axes
        plot_item.getAxis("left").setPen(pg.mkPen(color="black", width=2))
        plot_item.getAxis("bottom").setPen(pg.mkPen(color="black", width=2))

        # Customize the font of axis labels and tick marks
        axis_font = pg.Qt.QtGui.QFont("Times New Roman")
        axis_font.setPointSize(14)  # Set the font size for axis labels and tick marks
        plot_item.getAxis("left").setTickFont(axis_font)
        plot_item.getAxis("bottom").setTickFont(axis_font)

        # Customize the labels themselves
        plot_item.getAxis("left").setLabel(
            self.result_element.y_axis_title, **{"font-size": "18pt", "font-family": "Times New Roman"}
        )
        plot_item.getAxis("bottom").setLabel(
            self.result_element.x_axis_title, **{"font-size": "18pt", "font-family": "Times New Roman"}
        )

        self.plot_widget.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred))
        self.plot_widget.resize(
            self.result_element.general_plot_config.size_x, self.result_element.general_plot_config.size_y
        )
        self.plot_widget.plotItem.layout.activate()

    def on_range_changed(self, view_box, new_range):
        # Get the current ranges from the view box and store them in the config
        x_range = self.plot_widget.plotItem.viewRange()[0]
        y_range = self.plot_widget.plotItem.viewRange()[1]
        self.result_element.general_plot_config.x_range = x_range
        self.result_element.general_plot_config.y_range = y_range

    def restore_axis_ranges(self):
        # Restore the stored axis ranges
        x_range = self.result_element.general_plot_config.x_range
        y_range = self.result_element.general_plot_config.y_range
        if x_range and y_range:
            # self.plot_widget.plotItem.getViewBox().setAutoVisible(y=False)
            # self.plot_widget.plotItem.getViewBox().setPadding(0)
            self.plot_widget.plotItem.setXRange(x_range[0], x_range[1], padding=0)
            self.plot_widget.plotItem.setYRange(y_range[0], y_range[1], padding=0)
