from typing import List, Union

import attrs
from PySide6.QtGui import QColor

from src.common.result.classes.base_result import BaseResultElement


class Scatter:
    def __init__(self, x, y, label, scatter_plot_config=None):
        self.x = x
        self.y = y
        self.label = label
        self.scatter_plot_config = scatter_plot_config if scatter_plot_config else ScatterPlotConfig()


class Line:
    def __init__(self, x, y, label, line_plot_config=None):
        self.x = x
        self.y = y
        self.label = label
        self.line_plot_config = line_plot_config if line_plot_config else LinePlotConfig()


class Band:
    def __init__(self, x, y1, y2, label, band_plot_config=None):
        self.x = x
        self.y1 = y1
        self.y2 = y2
        self.label = label
        self.band_plot_config = band_plot_config if band_plot_config else BandPlotConfig()


@attrs.define
class ScatterPlotConfig:
    point_color: QColor = QColor(100, 100, 255, 200)
    outline_color: QColor = QColor(100, 100, 100, 50)
    marker_shape: str = "Circle"
    point_size: int = 8
    jitter_x: float = 0
    jitter_y: float = 0


@attrs.define
class LinePlotConfig:
    line_color: QColor = QColor(255, 0, 0, 200)
    line_width: int = 4
    line_style: str = "Solid"


@attrs.define
class BandPlotConfig:
    line_color: QColor = QColor(100, 100, 100, 50)
    fill_color: QColor = QColor(255, 0, 0, 50)


@attrs.define
class GeneralPlotConfig:
    background_color: QColor = QColor(255, 255, 255, 255)
    size_x: int = 600
    size_y: int = 500
    x_range: List[float] = None
    y_range: List[float] = None


class PlotResultElement(BaseResultElement):
    def __init__(
        self,
        settings_panel_index,
        general_plot_config: GeneralPlotConfig = None,
        tab_title="Plot Result Element",
        plot_id="1",
        plot_title="Correlation plot",
        x_axis_title="",
        y_axis_title="",
    ):
        super().__init__()
        self.general_plot_config = general_plot_config if general_plot_config else GeneralPlotConfig()
        self.title: str = tab_title
        self.class_id: str = "PlotResultElement"
        self.items: List[Union[Scatter, Line, Band]] = []
        self.plot_id = plot_id
        self.plot_title = plot_title
        self.x_axis_title = x_axis_title
        self.y_axis_title = y_axis_title
        self.settings_panel_index = settings_panel_index

    def set_plot_id(self, plot_id):
        self.plot_id = plot_id

    def set_plot_title(self, plot_title):
        self.plot_title = plot_title

    def set_x_axis_title(self, x_axis_title):
        self.x_axis_title = x_axis_title

    def set_y_axis_title(self, y_axis_title):
        self.y_axis_title = y_axis_title

    def render_plot_to_html(self, renderer):
        result_container = renderer(parent_widget=None, result_element=self)
        html = result_container.plot_widget.render_to_html()
        return html

    def get_html(self, renderer=None):
        return (
            f"<div><b> Figure {self.plot_id} </b> </div>"
            f'<div class="double-spacing font"><i>{self.plot_title}</i></div><br><br>'
        ) + self.render_plot_to_html(renderer)
