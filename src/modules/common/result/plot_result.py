#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import base64
import io
import logging
from typing import List, Tuple, Union

import numpy as np
from matplotlib import cbook
from matplotlib import pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication

from src.common.qcolor import Colors, rgba_tuple_from_rgb_and_a
from src.modules.common.result.base_result import BaseResultElement
from src.modules.correlation.table import format_r_apa
from src.pyside_ext.elements.base import BasePanelElement
from src.settings_panel.panels.result_item_settings_classes import (
    CheckboxResultItemSetting,
    ColorGridItemSetting,
    ContainerResultItemSetting,
    SingleLineTextResultItemSetting,
    SliderResultItemSetting,
)


class ContingencyPlot:
    def __init__(self, contingency_table, label, config=None):
        self.contingency_table = contingency_table
        self.label = label
        self.config = config if config else ContingencyPlotConfig()


class Scatter:
    def __init__(self, x, y, label, config=None):
        self.x = x
        self.y = y
        self.label = label
        self.config: ScatterPlotConfig = config if config else ScatterPlotConfig()


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


class BasePlotConfig:
    def __init__(self, **kwargs):
        self.display_settings = None

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("display_settings", None)

        for k, v in state.items():
            if isinstance(v, BasePanelElement):  # Todo make intermediate subclass
                state[k] = v.get_current_value()
        logging.warning(f"{state=}")
        return state

    def __setstate__(self, state):
        self.__init__(**state)


class ContingencyPlotConfig(BasePlotConfig):
    pass


class ScatterPlotConfig(BasePlotConfig):
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
        super().__init__()
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
        self.display_settings = ContainerResultItemSetting(
            items=[
                self.color,
                self.fill_alpha,
                self.line_alpha,
                self.point_size,
                self.jitter_x,
                self.jitter_y,
            ],
            add_stretch=True,
        )


class BarPlotConfig(BasePlotConfig):
    def __init__(self, color: Tuple[int, int, int] = Colors().get_color_list(), fill_alpha: int = 50):
        super().__init__()
        self.color: ColorGridItemSetting = ColorGridItemSetting(current_color=color)
        self.fill_alpha: SliderResultItemSetting = SliderResultItemSetting(
            label="Fill Alpha", current_value=fill_alpha, min_value=0, max_value=250, step=50
        )
        self.display_settings = ContainerResultItemSetting(
            items=[self.color, self.fill_alpha],
            add_stretch=True,
        )


class BoxPlotConfig(BasePlotConfig):
    def __init__(self, color: Tuple[int, int, int] = Colors().get_color_list(), fill_alpha: int = 50):
        super().__init__()
        self.color: ColorGridItemSetting = ColorGridItemSetting(current_color=color)
        self.fill_alpha: SliderResultItemSetting = SliderResultItemSetting(
            label="Fill Alpha", current_value=fill_alpha, min_value=0, max_value=250, step=50
        )
        self.display_settings = ContainerResultItemSetting(
            items=[self.color, self.fill_alpha],
            add_stretch=True,
        )


class LinePlotConfig(BasePlotConfig):
    def __init__(
        self,
        color: Tuple[int, int, int] = Colors().get_color_list(),
        line_alpha: int = 200,
        line_width: int = 3,
        line_style: str = "Solid",
    ):
        super().__init__()
        self.color: ColorGridItemSetting = ColorGridItemSetting(current_color=color)
        self.line_alpha: SliderResultItemSetting = SliderResultItemSetting(
            label="Line Alpha", current_value=line_alpha, min_value=0, max_value=250, step=50
        )
        self.line_width: SliderResultItemSetting = SliderResultItemSetting(
            label="Line Width", current_value=line_width, min_value=0, max_value=8, step=1
        )
        self.line_style = line_style
        self.display_settings = ContainerResultItemSetting(
            items=[self.color, self.line_alpha, self.line_width],
            add_stretch=True,
        )


class BandPlotConfig(BasePlotConfig):
    def __init__(self, color: Tuple[int, int, int] = Colors().get_color_list(), fill_alpha: int = 50):
        super().__init__()
        self.color: ColorGridItemSetting = ColorGridItemSetting(current_color=color)
        self.fill_alpha: SliderResultItemSetting = SliderResultItemSetting(
            label="Fill Alpha", current_value=fill_alpha, min_value=0, max_value=250, step=50
        )
        self.display_settings = ContainerResultItemSetting(
            items=[self.color, self.fill_alpha],
            add_stretch=True,
        )


class HeatmapPlotConfig(BasePlotConfig):
    def __init__(
        self, symmetric_color_scale: bool = True, only_significant: bool = False, alpha: float = 0.5, font_size=10
    ):
        super().__init__()
        self.symmetric_color_scale: CheckboxResultItemSetting = CheckboxResultItemSetting(
            label="Symmetric Color Scale",
            current_value=symmetric_color_scale,
        )
        self.only_significant: CheckboxResultItemSetting = CheckboxResultItemSetting(
            label="Significant Only",
            current_value=only_significant,
        )
        self.alpha: SliderResultItemSetting = SliderResultItemSetting(
            label="Alpha",
            current_value=alpha,
            min_value=0,
            max_value=1,
            step=0.1,
        )
        self.font_size: SliderResultItemSetting = SliderResultItemSetting(
            label="Font Size",
            current_value=font_size,
            min_value=5,
            max_value=20,
            step=1,
        )
        self.display_settings = ContainerResultItemSetting(
            items=[
                self.symmetric_color_scale,
                self.only_significant,
                self.alpha,
                self.font_size,
            ],
            add_stretch=True,
        )


class PlotV2(BaseResultElement):
    settings_panel_index = None

    def __init__(
        self,
        items: List[Union[Scatter, Line, Band, Bar, Box, Heatmap, ContingencyPlot]],
        title="Plot Result Element",
        plot_id="",
        plot_title="Correlation plot",
        x_axis_title="",
        y_axis_title="",
        x_axis_items=None,
        plot_x_size=600,
        plot_y_size=500,
        x_range: Tuple[float, float] = None,
        y_range: Tuple[float, float] = None,
        tilt_x_axis_labels=0,
    ):
        super().__init__()
        self.plot_x_size = plot_x_size
        self.plot_y_size = plot_y_size
        self.x_range = x_range
        self.y_range = y_range

        self.title: str = title
        self.class_id: str = "PlotV2"
        self.items = items if items else []
        self.x_axis_items = x_axis_items
        self.plot_id = SingleLineTextResultItemSetting(label="Number:", current_value=plot_id)
        self.plot_title = SingleLineTextResultItemSetting(label="Title:", current_value=plot_title)
        self.x_axis_title = SingleLineTextResultItemSetting(label="X axis title", current_value=x_axis_title)
        self.y_axis_title = SingleLineTextResultItemSetting(label="Y axis title", current_value=y_axis_title)
        self.tilt_x_axis_labels = SliderResultItemSetting(
            label="Rotate X Axis Labels",
            current_value=tilt_x_axis_labels,
            min_value=0,
            max_value=90,
            step=15,
        )
        self.display_settings = {
            "General": ContainerResultItemSetting(
                items=[
                    self.plot_id,
                    self.plot_title,
                    self.x_axis_title,
                    self.y_axis_title,
                    self.tilt_x_axis_labels,
                ],
                add_stretch=True,
            ),
        }

        for item in self.items:
            # if item has display_settings, add it
            if item.config.display_settings is not None:
                class_name = item.__class__.__name__
                label = class_name + ": " + item.label
                if label in self.display_settings:
                    raise ValueError(f"duplicated label found: {label}")
                self.display_settings[label] = item.config.display_settings

        # ===
        self._gc_ignore = []

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("display_settings", None)
        state.pop("class_id", None)
        state.pop("_gc_ignore", None)

        for k, v in state.items():
            if issubclass(type(v), BasePanelElement):
                state[k] = v.get_current_value()
        logging.warning(f"PlotV2 {state=}")
        return state

    def __setstate__(self, state):
        self.__init__(**state)

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
        legend = False

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
                    item.config.color.get_current_value(), item.config.line_alpha.get_current_value()
                )
                fill_color = rgba_tuple_from_rgb_and_a(
                    item.config.color.get_current_value(), item.config.fill_alpha.get_current_value()
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
                    item.config.color.get_current_value(), item.config.line_alpha.get_current_value()
                )

                if item.legend_string != "":
                    legend = True

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
                fill_color = rgba_tuple_from_rgb_and_a(
                    item.config.color.get_current_value(), item.config.fill_alpha.get_current_value()
                )

                ax.bar(
                    item.x,
                    item.y,
                    width=item.width,
                    color=fill_color,
                    linewidth=2,
                )

            if isinstance(item, Box):
                line_color = rgba_tuple_from_rgb_and_a(item.config.color.get_current_value(), 255)
                fill_color = rgba_tuple_from_rgb_and_a(
                    item.config.color.get_current_value(), item.config.fill_alpha.get_current_value()
                )
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
                fill_color = rgba_tuple_from_rgb_and_a(
                    item.config.color.get_current_value(), item.config.fill_alpha.get_current_value()
                )

                ax.fill_between(
                    item.x,
                    item.y1,
                    item.y2,
                    color=fill_color,
                    linewidth=0,
                )

            if isinstance(item, Heatmap):
                is_symmetric = item.config.symmetric_color_scale.get_current_value()
                alpha = item.config.alpha.get_current_value()
                if is_symmetric:
                    vmin = -max(abs(item.df.values.min()), abs(item.df.values.max()))
                    vmax = max(abs(item.df.values.min()), abs(item.df.values.max()))
                else:
                    vmin = item.df.values.min()
                    vmax = item.df.values.max()

                self._gc_ignore.append(
                    ax.imshow(
                        item.df,
                        cmap="bwr",
                        vmin=vmin,
                        vmax=vmax,
                        interpolation="nearest",
                        alpha=alpha,
                    )
                )
                # add colorbar
                ax.images[0].set_clim(vmin, vmax)
                fig.colorbar(ax.images[0], ax=ax, orientation="vertical")

                plt.xticks(range(len(item.df.columns)), item.df.columns)
                plt.yticks(range(len(item.df.index)), item.df.index)

                data = item.df
                # Adding annotations
                for i in range(len(data.index)):
                    for j in range(len(data.columns)):
                        if item.p is None or item.p.iloc[i, j] < 0.05 or not item.config.only_significant.get_current_value():
                            text = format_r_apa(data.iloc[i, j])  # + get_stars(item.p.iloc[i, j])

                            self._gc_ignore.append(
                                plt.text(
                                    j,
                                    i,
                                    text,
                                    ha="center",
                                    va="center",
                                    color="black",
                                    fontsize=item.config.font_size.get_current_value(),
                                )
                            )

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

        if legend:
            ax.legend()

        fig.tight_layout()
        return fig, ax

    # def get_html(self):
    #     fig, _ = self.create_figure()
    #     temp_svg_file_name = "./~tmp.svg"
    #     fig.savefig(temp_svg_file_name, format="svg", bbox_inches="tight")
    #     plt.close(fig)
    #     with open(temp_svg_file_name, "r", encoding="utf-8") as f:
    #         svg_data = f.read()
    #         base64_encoded_svg = (
    #             f"data:image/svg+xml;base64,{base64.b64encode(svg_data.encode('utf-8')).decode('utf-8')}"
    #         )
    #     os.remove(temp_svg_file_name)
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
        <div><b>Figure {self.plot_id.get_current_value()}</b></div>
        <div class="double-spacing font"><i>{self.plot_title.get_current_value()}</i></div><br>
        <img src="data:image/png;base64,{base64_png}"
             alt="Plot Image"
             style="width:400px; height:auto;">
        """
        return html

    def get_svg_buffer(self):
        fig, _ = self.create_figure()
        buf = io.BytesIO()
        fig.savefig(buf, format="svg", bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        return buf

    def get_png_buffer(self):
        fig, _ = self.create_figure()
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", dpi=150)
        plt.close(fig)
        buf.seek(0)
        return buf

    def copy_to_clipboard(self):
        buf = self.get_png_buffer()
        image = QImage.fromData(buf.getvalue(), "PNG")
        QApplication.clipboard().setImage(image)
        buf.close()
