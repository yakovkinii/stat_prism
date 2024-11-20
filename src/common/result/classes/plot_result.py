#
#  Copyright (c) 2023 -- 2024 StatPrism Team. All rights reserved.
#

import base64
import os
from typing import List, Tuple, Union

import attrs
import numpy as np
from matplotlib import cbook
from matplotlib import pyplot as plt

from src.common.qcolor import rgba_tuple_from_rgb_and_a
from src.common.result.classes.base_result import BaseResultElement
from src.common.utility import get_stars
from src.modules.correlation.table import format_r_apa


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
        stats,
        label,
        config=None,
    ):
        self.x_value = x_value
        self.stats = stats
        self.label = label
        self.config = config if config else BoxPlotConfig()

    @staticmethod
    def from_data(data, index, label, color):
        box_plot_config = BoxPlotConfig(color=color)

        stats = cbook.boxplot_stats(
            data,
            labels=[label],
        )

        plot_box = Box(
            x_value=index,
            stats=stats,
            config=box_plot_config,
            label=label,
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


class Heatmap:
    def __init__(self, df, p, label, config=None):
        self.df = df
        self.p = p
        self.label = label
        self.config = config if config else HeatmapPlotConfig()


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


MARKER_SHAPE_TO_MATPLOTLIB = {
    "Circle": "o",
    "Square": "s",
    "Diamond": "d",
    "Plus": "+",
    "Cross": "x",
    "Star": "*",
}

LINE_STYLE_TO_MATPLOTLIB = {
    "Solid": "-",
    "Dash": "--",
    "Dot": ":",
    "Dash-dot": "-.",
    "None": "",
}


@attrs.define
class ScatterPlotConfig:
    color: Tuple[int, int, int] = Colors().get_color_list()
    fill_alpha: int = 100
    line_alpha: int = 0
    marker_shape: str = "Circle"
    point_size: int = 8
    jitter_x: float = 0
    jitter_y: float = 0


@attrs.define
class BarPlotConfig:
    color: Tuple[int, int, int] = Colors().get_color_list()
    fill_alpha: int = 50


@attrs.define
class BoxPlotConfig:
    color: Tuple[int, int, int] = Colors().get_color_list()
    fill_alpha: int = 50


@attrs.define
class LinePlotConfig:
    color: Tuple[int, int, int] = Colors().get_color_list()
    line_alpha: int = 200
    line_width: int = 3
    line_style: str = "Solid"


@attrs.define
class BandPlotConfig:
    color: Tuple[int, int, int] = Colors().get_color_list()
    fill_alpha: int = 50


@attrs.define
class HeatmapPlotConfig:
    _ = None


@attrs.define
class GeneralPlotConfig:
    color: Tuple[int, int, int] = [255, 255, 255]
    transparent: bool = False
    size_x: int = 600
    size_y: int = 500
    x_range: Tuple[float, float] = None
    y_range: Tuple[float, float] = None
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

    def create_figure(self):
        fig, ax = plt.subplots()
        # set background color
        fig.patch.set_facecolor(rgba_tuple_from_rgb_and_a(self.general_plot_config.color, 255))
        ax.set_facecolor(rgba_tuple_from_rgb_and_a(self.general_plot_config.color, 255))

        dpi = fig.get_dpi()
        fig.set_size_inches(self.general_plot_config.size_x / dpi, self.general_plot_config.size_y / dpi)
        self.legend = False

        # self.restore_axis_ranges()
        # self.plot_widget.plotItem.vb.sigRangeChanged.connect(self.on_range_changed)

        for item in self.items:
            if isinstance(item, Scatter):
                np.random.seed(0)

                if item.config.jitter_x == 0:
                    x_data = item.x
                else:
                    amplitude = (item.x.max() - item.x.min()) * 0.1
                    if amplitude == 0:
                        amplitude = (abs(item.x.max()) + 1) * 0.1
                    x_data = item.x + item.config.jitter_x * (np.random.rand(len(item.x)) - 0.5) * amplitude

                if item.config.jitter_y == 0:
                    y_data = item.y
                else:
                    amplitude = (item.y.max() - item.y.min()) * 0.1
                    if amplitude == 0:
                        amplitude = (abs(item.y.max()) + 1) * 0.1
                    y_data = item.y + item.config.jitter_y * (np.random.rand(len(item.y)) - 0.5) * amplitude

                line_color = rgba_tuple_from_rgb_and_a(item.config.color, item.config.line_alpha)
                fill_color = rgba_tuple_from_rgb_and_a(item.config.color, item.config.fill_alpha)

                ax.scatter(
                    x_data,
                    y_data,
                    s=item.config.point_size**2,
                    marker=MARKER_SHAPE_TO_MATPLOTLIB[item.config.marker_shape],
                    edgecolors=line_color,
                    facecolors=fill_color,
                    linewidth=2,
                )

            if isinstance(item, Line):
                line_color = rgba_tuple_from_rgb_and_a(item.config.color, item.config.line_alpha)

                if item.legend_string != "":
                    self.legend = True

                ax.plot(
                    item.x,
                    item.y,
                    color=line_color,
                    linewidth=item.config.line_width,
                    linestyle=LINE_STYLE_TO_MATPLOTLIB[item.config.line_style],
                    label=item.legend_string if item.legend_string != "" else None,
                    solid_capstyle="round",
                )

            if isinstance(item, Bar):
                fill_color = rgba_tuple_from_rgb_and_a(item.config.color, item.config.fill_alpha)

                ax.bar(
                    item.x,
                    item.y,
                    width=item.width,
                    color=fill_color,
                    linewidth=2,
                )

            if isinstance(item, Box):
                line_color = rgba_tuple_from_rgb_and_a(item.config.color, 255)
                fill_color = rgba_tuple_from_rgb_and_a(item.config.color, item.config.fill_alpha)
                ax.bxp(
                    item.stats,
                    positions=[item.x_value],
                    widths=0.6,
                    patch_artist=True,
                    boxprops={
                        "facecolor": fill_color,
                        "edgecolor": line_color,
                        "linewidth": 1,
                    },
                    whiskerprops={
                        "color": line_color,
                        "linewidth": 2,
                        "solid_capstyle": "butt",
                    },
                    flierprops={
                        "color": line_color,
                        "marker": "o",
                        "markersize": 6,
                        "markerfacecolor": fill_color,
                        "markeredgecolor": line_color,
                        "solid_capstyle": "butt",
                    },
                    medianprops={
                        "color": line_color,
                        "linewidth": 3,
                        "solid_capstyle": "butt",
                    },
                    capprops={
                        "color": line_color,
                        "linewidth": 2,
                    },
                )

            if isinstance(item, Band):
                fill_color = rgba_tuple_from_rgb_and_a(item.config.color, item.config.fill_alpha)

                ax.fill_between(
                    item.x,
                    item.y1,
                    item.y2,
                    color=fill_color,
                    linewidth=0,
                )

            if isinstance(item, Heatmap):
                ax.imshow(item.df, cmap="coolwarm", vmin=-1, vmax=1, interpolation="nearest")
                plt.xticks(range(len(item.df.columns)), item.df.columns)
                plt.yticks(range(len(item.df.index)), item.df.index)

                data = item.df
                # Adding annotations
                for i in range(len(data.index)):
                    for j in range(len(data.columns)):
                        text = format_r_apa(data.iloc[i, j]) + get_stars(item.p.iloc[i, j])

                        plt.text(j, i, text, ha="center", va="center", color="grey", fontsize=14)

        # increase font size, set Times New Roman
        ax.tick_params(axis="both", which="major", labelsize=14, colors="grey")
        ax.spines["top"].set_color("grey")
        ax.spines["right"].set_color("grey")
        ax.spines["left"].set_color("grey")
        ax.spines["bottom"].set_color("grey")

        if self.x_axis_items is not None:
            ax.set_xticks(range(len(self.x_axis_items)))
            ax.set_xticklabels(self.x_axis_items)

        if self.general_plot_config.tilt_x_axis_labels:
            ax.tick_params(axis="x", rotation=45)

        # axis titles
        ax.set_xlabel(self.x_axis_title)
        ax.set_ylabel(self.y_axis_title)
        ax.xaxis.label.set_fontsize(18)
        ax.yaxis.label.set_fontsize(18)
        # set axis label font
        ax.xaxis.label.set_fontname("Times New Roman")
        ax.yaxis.label.set_fontname("Times New Roman")

        if self.general_plot_config.x_range is not None:
            ax.set_xlim(*self.general_plot_config.x_range)
        if self.general_plot_config.y_range is not None:
            ax.set_ylim(*self.general_plot_config.y_range)

        if self.legend:
            ax.legend()

        # set tight layout
        fig.tight_layout()
        return fig, ax

    def get_html(self):
        fig, _ = self.create_figure()

        temp_svg_file_name = "./~tmp.svg"
        fig.savefig(temp_svg_file_name, format="svg", bbox_inches="tight")
        plt.close(fig)

        with open(temp_svg_file_name, "r", encoding="utf-8") as f:
            svg_data = f.read()
            base64_encoded_svg = (
                f"data:image/svg+xml;base64,{base64.b64encode(svg_data.encode('utf-8')).decode('utf-8')}"
            )

        os.remove(temp_svg_file_name)

        result = f"""
            <div><b> Figure {self.plot_id} </b> </div>
            <div class="double-spacing font"><i>{self.plot_title}</i></div><br>
            <img src="{base64_encoded_svg}" alt="Plot Image" style="width: 400px; height: auto;">
        """
        return result
