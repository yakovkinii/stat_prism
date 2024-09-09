import pyqtgraph as pg
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget

from src.common.constant import MARKER_SHAPE_MAP, PEN_STYLE_MAP
from src.common.elements.resizeable_plot_widget.resizeable_plot_widget import ResizablePlotWidget
from src.common.elements.utility.layout_helpers import empty_widget
from src.common.result.classes.plot_result import Band, Line, PlotResultElement, Scatter


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
        self.label.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum))

        self.widget_layout.addWidget(self.label)

        self.plot_container = QWidget(self.widget)
        self.plot_container.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding))

        self.widget_layout.addWidget(self.plot_container)

        self.plot_widget = ResizablePlotWidget(self.plot_container, self.result_element)
        self.plot_widget.plotItem.setDefaultPadding(0.1)
        # l = pg.GraphicsLayout()
        # l.layout.setContentsMargins(10, 10, 10, 10)
        # self.plot_widget.setLayout(l)

        # add margins around the contents of plot_widget
        self.plot_widget.plotItem.layout.setContentsMargins(20, 20, 20, 20)

        self.plot_widget.setBackground(self.result_element.general_plot_config.background_color)

        self.items = []
        for item in self.result_element.items:
            if isinstance(item, Scatter):
                plot_item = pg.ScatterPlotItem(item.x, item.y, pen=None, symbol="o", brush="b")
                self.plot_widget.addItem(plot_item)

                plot_item.setBrush(pg.mkBrush(item.scatter_plot_config.point_color))
                plot_item.setPen(pg.mkPen(item.scatter_plot_config.outline_color))
                plot_item.setSymbol(MARKER_SHAPE_MAP[item.scatter_plot_config.marker_shape])
                plot_item.setSize(item.scatter_plot_config.point_size)

            if isinstance(item, Line):
                plot_item = self.plot_widget.plot(item.x, item.y)

                plot_item.setBrush(pg.mkBrush(item.line_plot_config.line_color))
                plot_item.setPen(
                    pg.mkPen(
                        item.line_plot_config.line_color,
                        width=item.line_plot_config.line_width,
                        style=PEN_STYLE_MAP[item.line_plot_config.line_style],
                    )
                )

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
