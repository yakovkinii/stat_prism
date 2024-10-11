from typing import List, Tuple, Union

import attrs
import numpy as np

from src.common.result.classes.base_result import BaseResultElement


class Scatter:
    def __init__(self, x, y, label, config=None):
        self.x = x
        self.y = y
        self.label = label
        self.config = config if config else ScatterPlotConfig()


class Bar:
    def __init__(self, x, y, width, label, config=None):
        self.x = x
        self.y = y
        self.width = width
        self.label = label
        self.config = config if config else BarPlotConfig()


class Box:
    def __init__(
        self,
        x_value,
        q1: float,
        q3: float,
        median: float,
        lower_whisker: float,
        upper_whisker: float,
        label,
        whiskers_only=False,
        config=None,
    ):
        self.x_value = x_value
        self.q1 = q1
        self.q3 = q3
        self.median = median
        self.lower_whisker = lower_whisker
        self.upper_whisker = upper_whisker
        self.label = label
        self.config = config if config else BoxPlotConfig()
        self.whiskers_only = whiskers_only

    @staticmethod
    def from_data(data, index, label, color):
        box_plot_config = BoxPlotConfig(color=color)
        iqr = np.percentile(data, 75) - np.percentile(data, 25)
        lower_whisker = np.max([np.min(data), np.percentile(data, 25) - 1.5 * iqr])
        upper_whisker = np.min([np.max(data), np.percentile(data, 75) + 1.5 * iqr])

        plot_box = Box(
            x_value=index,
            q1=np.percentile(data, 25),
            q3=np.percentile(data, 75),
            median=np.median(data),
            lower_whisker=lower_whisker,
            upper_whisker=upper_whisker,
            label=label,
            config=box_plot_config,
        )
        return plot_box

    @staticmethod
    def from_data_mean_std(data, index, label, color):
        box_plot_config = BoxPlotConfig(color=color)

        mean = np.mean(data)
        std = np.std(data)
        lower_whisker = mean - std
        upper_whisker = mean + std

        plot_box = Box(
            x_value=index,
            q1=0,
            q3=0,
            median=mean,
            lower_whisker=lower_whisker,
            upper_whisker=upper_whisker,
            label=label,
            config=box_plot_config,
            whiskers_only=True,
        )
        return plot_box


class Line:
    def __init__(self, x, y, label, legend_string: str = "", config=None):
        self.x = x
        self.y = y
        self.legend_string = legend_string
        self.label = label
        self.config = config if config else LinePlotConfig()


class Band:
    def __init__(self, x, y1, y2, label, config=None):
        self.x = x
        self.y1 = y1
        self.y2 = y2
        self.label = label
        self.config = config if config else BandPlotConfig()


class Colors:
    def __init__(self):
        self.colors = [
            [100, 100, 255],
            [255, 100, 100],
            [100, 200, 100],
            [255, 100, 0],
            [200, 100, 200],
            [100, 200, 200],
            [100, 100, 100],
        ]
        self.index = 0

    def get_color_list(self):
        color = self.colors[self.index]
        self.index += 1
        if self.index >= len(self.colors):
            self.index = 0
        return color


@attrs.define
class ScatterPlotConfig:
    color: Tuple[int, int, int] = Colors().get_color_list()
    fill_alpha: int = 50
    line_alpha: int = 200
    marker_shape: str = "Circle"
    point_size: int = 8
    jitter_x: float = 0
    jitter_y: float = 0


@attrs.define
class BarPlotConfig:
    color: Tuple[int, int, int] = Colors().get_color_list()
    fill_alpha: int = 50
    line_alpha: int = 200


@attrs.define
class BoxPlotConfig:
    color: Tuple[int, int, int] = Colors().get_color_list()
    fill_alpha: int = 50
    line_alpha: int = 200


@attrs.define
class LinePlotConfig:
    color: Tuple[int, int, int] = Colors().get_color_list()
    line_alpha: int = 200
    line_width: int = 4
    line_style: str = "Solid"


@attrs.define
class BandPlotConfig:
    color: Tuple[int, int, int] = Colors().get_color_list()
    fill_alpha: int = 50
    line_alpha: int = 200


@attrs.define
class GeneralPlotConfig:
    color: Tuple[int, int, int] = [255, 255, 255]
    alpha: int = 255
    size_x: int = 600
    size_y: int = 500
    x_range: List[float] = None
    y_range: List[float] = None
    tilt_x_axis_labels: bool = False


class PlotResultElement(BaseResultElement):
    def __init__(
        self,
        settings_panel_index,
        general_plot_config: GeneralPlotConfig = None,
        tab_title="Plot Result Element",
        plot_id="",
        plot_title="Correlation plot",
        x_axis_title="",
        y_axis_title="",
        x_axis_items=None,
    ):
        super().__init__()
        self.general_plot_config = general_plot_config if general_plot_config else GeneralPlotConfig()
        self.title: str = tab_title
        self.class_id: str = "PlotResultElement"
        self.items: List[Union[Scatter, Line, Band, Bar, Box]] = []
        self.plot_id = plot_id
        self.plot_title = plot_title
        self.x_axis_title = x_axis_title
        self.y_axis_title = y_axis_title
        self.settings_panel_index = settings_panel_index
        self.x_axis_items = x_axis_items

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
            f'<div class="double-spacing font"><i>{self.plot_title}</i></div><br>'
        ) + self.render_plot_to_html(renderer)
