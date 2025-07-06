#
#  Copyright (c) 2023 -- 2024 StatPrism Team. All rights reserved.
#

import base64
import io
import logging
from typing import List, Tuple, Union

import attrs
import numpy as np
from matplotlib import cbook
from matplotlib import pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

from src.common.qcolor import Colors, rgba_tuple_from_rgb_and_a
from src.common.result.classes.base_result import BaseResultElement
from src.modules.correlation.table import format_r_apa
from src.settings_panel.panels.result_item_settings_v2.classes import (
    CheckboxResultItemSetting,
    ColorGridItemSetting,
    ContainerResultItemSetting,
    NumberCaptionResultItemSetting,
    SingleLineTextResultItemSetting,
    SliderResultItemSetting,
)


class ContingencyPlot:
    def __init__(self, contingency_table, label, config=None):
        self.contingency_table = contingency_table
        self.label = label
        self.config = config if config else ContingencyPlotConfig()
        self.display_settings = None


class Scatter:
    def __init__(self, x, y, label, config=None):
        self.x = x
        self.y = y
        self.label = label
        self.config: ScatterPlotConfig = config if config else ScatterPlotConfig()
        self.display_settings = ContainerResultItemSetting(
            items=[
                self.config.color,
                self.config.fill_alpha,
                self.config.line_alpha,
                self.config.point_size,
                self.config.jitter_x,
                self.config.jitter_y,
            ],
            add_stretch=True,
        )


class Bar:
    def __init__(self, x, y, width, label, config=None):
        self.x = x
        self.y = y
        self.width = width
        self.label = label
        self.config = config if config else BarPlotConfig()
        self.display_settings = None


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
        self.display_settings = None

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
        self.display_settings = ContainerResultItemSetting(
            items=[
                self.config.color,
                self.config.line_alpha,
                self.config.line_width,
            ],
            add_stretch=True,
        )


class Band:
    def __init__(self, x, y1, y2, label, config=None):
        self.x = x
        self.y1 = y1
        self.y2 = y2
        self.label = label
        self.config = config if config else BandPlotConfig()
        self.display_settings = None


class Heatmap:
    def __init__(self, df, p, label, config=None):
        self.df = df
        self.p = p
        self.label = label
        self.config = config if config else HeatmapPlotConfig()
        self.display_settings = ContainerResultItemSetting(
            items=[self.config.symmetric_color_scale, self.config.color_scale_padding],
            add_stretch=True,
        )


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
class ContingencyPlotConfig:
    ...
    # color: Tuple[int, int, int] = Colors().get_color_list()
    # fill_alpha: int = 100
    # line_alpha: int = 0
    # marker_shape: str = "Circle"
    # point_size: int = 8
    # jitter_x: float = 0
    # jitter_y: float = 0


class ScatterPlotConfig:
    def __init__(
        self,
        color: Tuple[int, int, int] = Colors().get_color_list(),
        fill_alpha: int = 100,
        line_alpha: int = 0,
        marker_shape: str = "Circle",
        point_size: int = 8,
        jitter_x: float = 0,
        jitter_y: float = 0,
    ):
        self.color: ColorGridItemSetting = ColorGridItemSetting(current_color=color)
        self.fill_alpha: SliderResultItemSetting = SliderResultItemSetting(
            label="Fill Alpha", current_value=fill_alpha, min_value=0, max_value=250, step=50
        )
        self.line_alpha: SliderResultItemSetting = SliderResultItemSetting(
            label="Line Alpha", current_value=line_alpha, min_value=0, max_value=250, step=50
        )
        self.marker_shape: str = marker_shape
        self.point_size: SliderResultItemSetting = SliderResultItemSetting(
            label="Point Size", current_value=point_size, min_value=0, max_value=16, step=1
        )
        self.jitter_x: SliderResultItemSetting = SliderResultItemSetting(
            label="Jitter X", current_value=jitter_x, min_value=0, max_value=2, step=0.2
        )
        self.jitter_y: SliderResultItemSetting = SliderResultItemSetting(
            label="Jitter Y", current_value=jitter_y, min_value=0, max_value=2, step=0.2
        )


@attrs.define
class BarPlotConfig:
    color: Tuple[int, int, int] = Colors().get_color_list()
    fill_alpha: int = 50


@attrs.define
class BoxPlotConfig:
    color: Tuple[int, int, int] = Colors().get_color_list()
    fill_alpha: int = 50


class LinePlotConfig:
    def __init__(
        self,
        color: Tuple[int, int, int] = Colors().get_color_list(),
        line_alpha: int = 200,
        line_width: int = 3,
        line_style: str = "Solid",
    ):
        self.color: ColorGridItemSetting = ColorGridItemSetting(current_color=color)
        self.line_alpha: SliderResultItemSetting = SliderResultItemSetting(
            label="Line Alpha", current_value=line_alpha, min_value=0, max_value=250, step=50
        )
        self.line_width: SliderResultItemSetting = SliderResultItemSetting(
            label="Line Width", current_value=line_width, min_value=0, max_value=8, step=1
        )
        self.line_style = line_style


@attrs.define
class BandPlotConfig:
    color: Tuple[int, int, int] = Colors().get_color_list()
    fill_alpha: int = 50


class HeatmapPlotConfig:
    def __init__(self, symmetric_color_scale: bool = True, scale_padding: float = 0.5):
        self.symmetric_color_scale: CheckboxResultItemSetting = CheckboxResultItemSetting(
            label="Symmetric Color Scale",
            current_value=symmetric_color_scale,
        )
        self.color_scale_padding: SliderResultItemSetting = SliderResultItemSetting(
            label="Scale Padding",
            current_value=scale_padding,
            min_value=0,
            max_value=1,
            step=0.1,
        )


@attrs.define
class GeneralPlotConfig:
    color: Tuple[int, int, int] = [255, 255, 255]
    transparent: bool = False
    size_x: int = 600
    size_y: int = 500
    x_range: Tuple[float, float] = None
    y_range: Tuple[float, float] = None
    tilt_x_axis_labels: bool = False


class PlotV2(BaseResultElement):
    settings_panel_index = None

    def __init__(
        self,
        items: List[Union[Scatter, Line, Band, Bar, Box, Heatmap, ContingencyPlot]],
        tab_title="Plot Result Element",
        plot_id="",
        plot_title="Correlation plot",
        x_axis_title="",
        y_axis_title="",
        x_axis_items=None,
    ):
        super().__init__(v2=True)
        # Static for now
        self.plot_x_size = 600
        self.plot_y_size = 500

        self.x_range = None
        self.y_range = None

        # Dynamic
        self.title: str = tab_title
        self.class_id: str = "PlotV2"
        self.items = items if items else []
        self.plot_id = plot_id
        self.plot_title = plot_title
        self.x_axis_items = x_axis_items
        self.number_caption = NumberCaptionResultItemSetting(current_number=plot_id, current_caption=plot_title)
        self.x_axis_title = SingleLineTextResultItemSetting(label="X axis title", current_value=x_axis_title)
        self.y_axis_title = SingleLineTextResultItemSetting(label="Y axis title", current_value=y_axis_title)
        self.tilt_x_axis_labels = SliderResultItemSetting(
            label="Rotate X Axis Labels",
            current_value=0,
            min_value=0,
            max_value=90,
            step=15,
        )
        self.display_settings = {
            "General": ContainerResultItemSetting(
                items=[
                    self.number_caption,
                    self.x_axis_title,
                    self.y_axis_title,
                    self.tilt_x_axis_labels,
                ],
                add_stretch=True,
            ),
        }

        for item in self.items:
            # if item has display_settings, add it
            if item.display_settings is not None:
                class_name = item.__class__.__name__
                label = class_name + ": " + item.label
                if label in self.display_settings:
                    raise ValueError(f"duplicated label found: {label}")
                self.display_settings[label] = item.display_settings

        # ===
        self._gc_ignore = []

    def create_figure(self):
        plt.close("all")
        fig, ax = plt.subplots()
        # self._gc_ignore.append(fig)
        # self._gc_ignore.append(ax)

        # set background color
        face_color = (255, 255, 255)
        fig.patch.set_facecolor(rgba_tuple_from_rgb_and_a(face_color, 255))
        ax.set_facecolor(rgba_tuple_from_rgb_and_a(face_color, 255))

        dpi = fig.get_dpi()
        fig.set_size_inches(self.plot_x_size / dpi, self.plot_y_size / dpi)
        self.legend = False

        for item in self.items:
            if isinstance(item, Scatter):
                np.random.seed(0)

                if item.config.jitter_x.get_current_value() == 0:
                    x_data = item.x
                else:
                    amplitude = (item.x.max() - item.x.min()) * 0.1
                    if amplitude == 0:
                        amplitude = (abs(item.x.max()) + 1) * 0.1
                    x_data = (
                        item.x
                        + item.config.jitter_x.get_current_value() * (np.random.rand(len(item.x)) - 0.5) * amplitude
                    )

                if item.config.jitter_y.get_current_value() == 0:
                    y_data = item.y
                else:
                    amplitude = (item.y.max() - item.y.min()) * 0.1
                    if amplitude == 0:
                        amplitude = (abs(item.y.max()) + 1) * 0.1
                    y_data = (
                        item.y
                        + item.config.jitter_y.get_current_value() * (np.random.rand(len(item.y)) - 0.5) * amplitude
                    )

                line_color = rgba_tuple_from_rgb_and_a(
                    item.config.color.get_current_color(), item.config.line_alpha.get_current_value()
                )
                fill_color = rgba_tuple_from_rgb_and_a(
                    item.config.color.get_current_color(), item.config.fill_alpha.get_current_value()
                )

                ax.scatter(
                    x_data,
                    y_data,
                    s=item.config.point_size.get_current_value() ** 2,
                    marker=MARKER_SHAPE_TO_MATPLOTLIB[item.config.marker_shape],
                    edgecolors=line_color,
                    facecolors=fill_color,
                    linewidth=2,
                )

            if isinstance(item, Line):
                line_color = rgba_tuple_from_rgb_and_a(
                    item.config.color.get_current_color(), item.config.line_alpha.get_current_value()
                )

                if item.legend_string != "":
                    self.legend = True

                ax.plot(
                    item.x,
                    item.y,
                    color=line_color,
                    linewidth=item.config.line_width.get_current_value(),
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
                is_symmetric = item.config.symmetric_color_scale.get_current_value()
                scale_padding = item.config.color_scale_padding.get_current_value()
                if is_symmetric:
                    vmin = -max(abs(item.df.values.min()), abs(item.df.values.max()))
                    vmax = max(abs(item.df.values.min()), abs(item.df.values.max()))
                else:
                    vmin = item.df.values.min()
                    vmax = item.df.values.max()


                if scale_padding == 1:
                    a=1
                self._gc_ignore.append(ax.imshow(
                    item.df, cmap="bwr", vmin=vmin - scale_padding, vmax=vmax + scale_padding, interpolation="nearest"
                ))
                # add colorbar
                # fig.colorbar(ax.images[0], ax=ax, orientation="vertical", fraction=0.046, pad=0.04)

                plt.xticks(range(len(item.df.columns)), item.df.columns)
                plt.yticks(range(len(item.df.index)), item.df.index)

                data = item.df
                # Adding annotations
                for i in range(len(data.index)):
                    for j in range(len(data.columns)):
                        if item.p.iloc[i, j] < 0.05:
                            text = format_r_apa(data.iloc[i, j])  # + get_stars(item.p.iloc[i, j])

                            self._gc_ignore.append(plt.text(
                                j,
                                i,
                                text,
                                ha="center",
                                va="center",
                                color="black",
                                fontsize=8,
                                # bbox=dict(facecolor="white", alpha=0.6, boxstyle="round,pad=0.2", edgecolor='none'),
                            ))

            if isinstance(item, ContingencyPlot):
                contingency_table = item.contingency_table
                total_number = contingency_table.sum().sum()
                # Create a 100% stacked bar chart
                data_pct = contingency_table / contingency_table.sum() * 100
                totals_frac = contingency_table.sum(axis=1) / total_number * 100
                bar_widths = contingency_table.sum() / total_number
                positions_non_centered = (bar_widths.cumsum() + bar_widths.cumsum().shift(1, fill_value=0)) / 2
                positions = [bar_width - bar_widths.iloc[0] / 2 for bar_width in positions_non_centered]
                color_manager = Colors()
                colors = [rgba_tuple_from_rgb_and_a(color_manager.get_color_list(), 255) for _ in range(len(data_pct))]

                # Plot the stacked bar chart accounting for widths of each bar
                for j, col in enumerate(data_pct.columns):
                    bottom = 0
                    for i, row in enumerate(data_pct.index):
                        ax.bar(
                            positions[j],
                            data_pct.iloc[i, j],
                            bottom=bottom,
                            color=colors[i],
                            align="center",
                            edgecolor="white",
                            width=bar_widths[col],
                            label=col if i == 0 else None,  # Only label the first bar
                        )
                        bottom += data_pct.iloc[i, j]
                # Set the x-ticks to the positions of the bars
                ax.set_xticks(positions)
                ax.set_xticklabels(data_pct.columns)

                ax.set_ylim(0, 100)
                ax.set_xlim(-bar_widths.iloc[0] / 2, positions[-1] + bar_widths.iloc[-1] / 2)

                divider = make_axes_locatable(ax)
                ax2 = divider.append_axes("right", size="5%", pad=0.1)

                ax2.set_anchor("S")
                bottom = 0
                midpoints = []
                for frac, c in zip(totals_frac, colors):
                    ax2.bar(0, frac, bottom=bottom, color=c, edgecolor="white", width=0.1)
                    midpoints.append(bottom + frac / 2)
                    bottom += frac
                # Clean up
                ax2.set_xlim(-0.05, 0.05)
                ax2.set_xticks([])
                ax2.set_ylim(0, 100)
                # place one tick per segment, at its midpoint
                ax2.set_yticks(midpoints)
                ax2.set_yticklabels(contingency_table.index)
                # y ticks on the right
                ax2.yaxis.tick_right()
                ax2.spines["left"].set_visible(False)
                ax2.spines["right"].set_color("grey")
                ax2.spines["top"].set_visible(False)
                ax2.spines["bottom"].set_visible(False)

        # increase font size, set Times New Roman
        ax.tick_params(axis="both", which="major", labelsize=14, colors="grey")
        ax.spines["top"].set_color("grey")
        ax.spines["right"].set_color("grey")
        ax.spines["left"].set_color("grey")
        ax.spines["bottom"].set_color("grey")

        if self.x_axis_items is not None:
            ax.set_xticks(range(len(self.x_axis_items)))
            ax.set_xticklabels(self.x_axis_items)

        ax.tick_params(axis="x", rotation=self.tilt_x_axis_labels.current_value)

        # axis titles
        ax.set_xlabel(self.x_axis_title.get_current_value())
        ax.set_ylabel(self.y_axis_title.get_current_value())
        ax.xaxis.label.set_fontsize(18)
        ax.yaxis.label.set_fontsize(18)
        # set axis label font
        ax.xaxis.label.set_fontname("Times New Roman")
        ax.yaxis.label.set_fontname("Times New Roman")

        # set axis ranges
        if self.x_range is not None:
            ax.set_xlim(*self.x_range)
        if self.y_range is not None:
            ax.set_ylim(*self.y_range)

        if self.legend:
            ax.legend()

        fig.tight_layout()
        return fig, ax

    # def get_html(self):
    #     fig, _ = self.create_figure()
    #
    #     temp_svg_file_name = "./~tmp.svg"
    #     fig.savefig(temp_svg_file_name, format="svg", bbox_inches="tight")
    #     plt.close(fig)
    #
    #     with open(temp_svg_file_name, "r", encoding="utf-8") as f:
    #         svg_data = f.read()
    #         base64_encoded_svg = (
    #             f"data:image/svg+xml;base64,{base64.b64encode(svg_data.encode('utf-8')).decode('utf-8')}"
    #         )
    #
    #     os.remove(temp_svg_file_name)
    #
    #     result = f"""
    #         <div><b> Figure {self.number_caption.get_number()} </b> </div>
    #         <div class="double-spacing font"><i>{self.number_caption.get_caption()}</i></div><br>
    #         <img src="{base64_encoded_svg}" alt="Plot Image" style="width: 400px; height: auto;">
    #     """
    #     return result

    def get_html(self):
        # 1) create your figure as before
        fig, _ = self.create_figure()

        # 2) dump it into an in-memory bytes buffer as PNG
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", dpi=150)
        plt.close(fig)
        buf.seek(0)

        # 3) base64-encode the PNG bytes
        png_bytes = buf.getvalue()
        base64_png = base64.b64encode(png_bytes).decode("ascii")
        buf.close()

        # 4) embed into an <img> tag
        html = f"""
        <div><b>Figure {self.number_caption.get_number()}</b></div>
        <div class="double-spacing font"><i>{self.number_caption.get_caption()}</i></div><br>
        <img src="data:image/png;base64,{base64_png}"
             alt="Plot Image"
             style="width:400px; height:auto;">
        """
        return html
