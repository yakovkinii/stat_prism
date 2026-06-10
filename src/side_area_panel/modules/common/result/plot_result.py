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
from src.common.theme import THEME
from src.pyside_ext.elements.base import BasePanelElement
from src.side_area_panel.modules.common.result.base_result import BaseResultElement
from src.side_area_panel.modules.common.utility import format_r_apa
from src.side_area_panel.panels.result_item_settings_classes import (
    CheckboxResultItemSetting,
    ColorGridItemSetting,
    ContainerResultItemSetting,
    DropdownResultItemSetting,
    PlainCheckboxResultItemSetting,
    SingleLineTextResultItemSetting,
    SliderResultItemSetting,
)

# Axis-title layout presets. Titles can be long, so these control where the x/y
# titles sit and whether the y title is rotated.
#   Centered: classic centered titles, y rotated vertical.
#   Edges:    x title pushed right, y title pushed to the top (still vertical).
#   Flat Y:   x title pushed right, y title horizontal above the axis, pushed left.
AXIS_LAYOUTS = ["Centered", "Edges", "Flat Y"]

# Gridline modes.
GRIDLINES = ["None", "Both", "Horizontal", "Vertical"]


class ContingencyPlot:
    def __init__(self, contingency_table, label, config=None):
        self.contingency_table = contingency_table
        self.label = label
        self.config = config if config else ContingencyPlotConfig()


class Pie:
    def __init__(self, labels, values, label, config=None):
        self.labels = labels
        self.values = values
        self.label = label
        self.config = config if config else PiePlotConfig()


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

        # Flatten settings to current values; persist their defaults in parallel.
        setting_defaults = {}
        for k, v in list(state.items()):
            if isinstance(v, BasePanelElement) and hasattr(v, "get_current_value"):
                setting_defaults[k] = v.get_default_value()
                state[k] = v.get_current_value()
        state["_setting_defaults"] = setting_defaults
        return state

    def __setstate__(self, state):
        setting_defaults = state.pop("_setting_defaults", {})
        self.__init__(**state)
        for k, default in setting_defaults.items():
            setting = getattr(self, k, None)
            if setting is not None and hasattr(setting, "set_default_value"):
                setting.set_default_value(default)


class ContingencyPlotConfig(BasePlotConfig):
    pass


class PiePlotConfig(BasePlotConfig):
    pass


class ScatterPlotConfig(BasePlotConfig):
    def __init__(
        self,
        color: Tuple[int, int, int] = None,
        fill_alpha: int = None,
        line_alpha: int = None,
        marker_shape: str = None,
        point_size: int = None,
        jitter_x: float = 0,
        jitter_y: float = 0,
    ):
        super().__init__()
        theme = THEME.current
        color = color if color is not None else Colors().get_color_list()
        fill_alpha = fill_alpha if fill_alpha is not None else theme.scatter_fill_alpha
        line_alpha = line_alpha if line_alpha is not None else theme.scatter_line_alpha
        marker_shape = marker_shape if marker_shape is not None else theme.marker_shape
        point_size = point_size if point_size is not None else theme.point_size
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
    def __init__(self, color: Tuple[int, int, int] = None, fill_alpha: int = None):
        super().__init__()
        theme = THEME.current
        color = color if color is not None else Colors().get_color_list()
        fill_alpha = fill_alpha if fill_alpha is not None else theme.bar_fill_alpha
        self.color: ColorGridItemSetting = ColorGridItemSetting(current_color=color)
        self.fill_alpha: SliderResultItemSetting = SliderResultItemSetting(
            label="Fill Alpha", current_value=fill_alpha, min_value=0, max_value=250, step=50
        )
        self.display_settings = ContainerResultItemSetting(
            items=[self.color, self.fill_alpha],
            add_stretch=True,
        )


class BoxPlotConfig(BasePlotConfig):
    def __init__(self, color: Tuple[int, int, int] = None, fill_alpha: int = None):
        super().__init__()
        theme = THEME.current
        color = color if color is not None else Colors().get_color_list()
        fill_alpha = fill_alpha if fill_alpha is not None else theme.box_fill_alpha
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
        color: Tuple[int, int, int] = None,
        line_alpha: int = None,
        line_width: int = None,
        line_style: str = None,
    ):
        super().__init__()
        theme = THEME.current
        color = color if color is not None else Colors().get_color_list()
        line_alpha = line_alpha if line_alpha is not None else theme.line_alpha
        line_width = line_width if line_width is not None else theme.line_width
        line_style = line_style if line_style is not None else theme.line_style
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
    def __init__(self, color: Tuple[int, int, int] = None, fill_alpha: int = None):
        super().__init__()
        theme = THEME.current
        color = color if color is not None else Colors().get_color_list()
        fill_alpha = fill_alpha if fill_alpha is not None else theme.band_fill_alpha
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
        items: List[Union[Scatter, Line, Band, Bar, Box, Heatmap, ContingencyPlot, Pie]],
        title="Plot Result Element",
        plot_title="Correlation plot",
        x_axis_title="",
        y_axis_title="",
        x_axis_items=None,
        plot_size=None,
        plot_aspect=None,
        x_range: Tuple[float, float] = None,
        y_range: Tuple[float, float] = None,
        tilt_x_axis_labels=0,
        axis_title_font_size=None,
        tick_label_font_size=None,
        legend_font_size=None,
        frame_thickness=None,
        frame_color: Tuple[int, int, int] = None,
        background_color: Tuple[int, int, int] = None,
        background_alpha=None,
        axis_layout=None,
        margin=None,
        box_frame=None,
        gridlines=None,
    ):
        super().__init__()
        # Defaults come from the active theme unless explicitly provided (e.g. restored
        # from a saved state). Each setting records the value it is created with as its
        # own default (see _ValueDefaultsMixin), which drives reset and the
        # carry-over-only-if-modified behaviour in load_settings_from.
        theme = THEME.current
        plot_size = plot_size if plot_size is not None else theme.plot_size
        plot_aspect = plot_aspect if plot_aspect is not None else theme.plot_aspect
        axis_title_font_size = axis_title_font_size if axis_title_font_size is not None else theme.axis_title_font_size
        tick_label_font_size = tick_label_font_size if tick_label_font_size is not None else theme.tick_label_font_size
        legend_font_size = legend_font_size if legend_font_size is not None else theme.legend_font_size
        frame_thickness = frame_thickness if frame_thickness is not None else theme.frame_thickness
        frame_color = frame_color if frame_color is not None else theme.frame_color
        background_color = background_color if background_color is not None else theme.background_color
        background_alpha = background_alpha if background_alpha is not None else theme.background_alpha
        axis_layout = axis_layout if axis_layout is not None else theme.axis_layout
        margin = margin if margin is not None else theme.margin
        box_frame = box_frame if box_frame is not None else theme.box_frame
        gridlines = gridlines if gridlines is not None else theme.gridlines

        self.x_range = x_range
        self.y_range = y_range

        self.title: str = title
        self.class_id: str = "PlotV2"
        self.items = items if items else []
        self.x_axis_items = x_axis_items
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
        # --- Figure-level appearance (applies to every plot type) ---
        self.plot_size = SliderResultItemSetting(
            label="Plot Size", current_value=plot_size, min_value=200, max_value=1400, step=50
        )
        self.plot_aspect = SliderResultItemSetting(
            label="Aspect (H/W)", current_value=plot_aspect, min_value=0.3, max_value=2.0, step=0.1
        )
        self.axis_title_font_size = SliderResultItemSetting(
            label="Axis Title Size", current_value=axis_title_font_size, min_value=6, max_value=30, step=1
        )
        self.tick_label_font_size = SliderResultItemSetting(
            label="Tick Label Size", current_value=tick_label_font_size, min_value=6, max_value=30, step=1
        )
        self.legend_font_size = SliderResultItemSetting(
            label="Legend Size", current_value=legend_font_size, min_value=6, max_value=30, step=1
        )
        self.frame_thickness = SliderResultItemSetting(
            label="Frame Thickness", current_value=frame_thickness, min_value=0, max_value=5, step=0.5
        )
        self.margin = SliderResultItemSetting(
            label="Margin", current_value=margin, min_value=0, max_value=2.0, step=0.1
        )
        self.frame_color = ColorGridItemSetting(current_color=frame_color, label="Frame / Tick Color")
        self.background_color = ColorGridItemSetting(current_color=background_color, label="Background Color")
        self.background_alpha = SliderResultItemSetting(
            label="Background Alpha", current_value=background_alpha, min_value=0, max_value=255, step=15
        )
        self.axis_layout = DropdownResultItemSetting(
            label="Axis layout", current_value=axis_layout, items=AXIS_LAYOUTS
        )
        self.box_frame = PlainCheckboxResultItemSetting(label="Full box frame (top/right)", current_value=box_frame)
        self.gridlines = DropdownResultItemSetting(
            label="Gridlines", current_value=gridlines, items=GRIDLINES
        )
        self.display_settings = {
            "General": ContainerResultItemSetting(
                items=[
                    self.plot_title,
                    self.x_axis_title,
                    self.y_axis_title,
                    self.axis_layout,
                    self.tilt_x_axis_labels,
                    self.plot_size,
                    self.plot_aspect,
                    self.margin,
                    self.axis_title_font_size,
                    self.tick_label_font_size,
                    self.legend_font_size,
                    self.frame_thickness,
                    self.box_frame,
                    self.gridlines,
                    self.frame_color,
                    self.background_color,
                    self.background_alpha,
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

    def _value_settings(self):
        """All value-holding settings in a stable order: figure-level first, then each
        series' config settings. Self and a sibling plot built the same way share this
        order, so they can be zipped for load_settings_from."""
        settings = []
        for value in self.__dict__.values():
            if isinstance(value, BasePanelElement) and hasattr(value, "get_current_value"):
                settings.append(value)
        for item in self.items:
            for value in item.config.__dict__.values():
                if isinstance(value, BasePanelElement) and hasattr(value, "get_current_value"):
                    settings.append(value)
        return settings

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("display_settings", None)
        state.pop("class_id", None)
        state.pop("_gc_ignore", None)

        # Flatten settings to their current value for pickling, and persist their
        # defaults in parallel so a reloaded project still knows each setting's default.
        setting_defaults = {}
        for k, v in list(state.items()):
            if isinstance(v, BasePanelElement) and hasattr(v, "get_current_value"):
                setting_defaults[k] = v.get_default_value()
                state[k] = v.get_current_value()
        state["_setting_defaults"] = setting_defaults
        return state

    def __setstate__(self, state):
        setting_defaults = state.pop("_setting_defaults", {})
        self.__init__(**state)
        for k, default in setting_defaults.items():
            setting = getattr(self, k, None)
            if setting is not None and hasattr(setting, "set_default_value"):
                setting.set_default_value(default)

    def load_settings_from(self, plot: "PlotV2"):
        """Carry the user's edits from a previous build onto this freshly-built plot.
        This plot already holds the current theme/module defaults; we only override a
        setting when the cached one was actually changed from its own default. So
        untouched settings adopt the new defaults (e.g. on a theme switch) while the
        user's explicit tweaks are preserved."""
        try:
            for new_setting, old_setting in zip(self._value_settings(), plot._value_settings()):
                if old_setting.is_modified():
                    new_setting.set_up_from_other_instance(old_setting)
        except Exception as e:
            logging.warning(f"Error trying to set settings from another plot: {e}")

    def reset_to_defaults(self):
        """Reset every setting to the default it was created with."""
        for setting in self._value_settings():
            setting.restore_default_value()

    def create_figure(self):
        plt.close("all")
        fig, ax = plt.subplots()
        # self._gc_ignore.append(fig)
        # self._gc_ignore.append(ax)

        # set background color
        face_color = self.background_color.get_current_value()
        bg_alpha = self.background_alpha.get_current_value()
        fig.patch.set_facecolor(rgba_tuple_from_rgb_and_a(face_color, bg_alpha))
        ax.set_facecolor(rgba_tuple_from_rgb_and_a(face_color, bg_alpha))

        dpi = fig.get_dpi()
        width = self.plot_size.get_current_value()
        height = width * self.plot_aspect.get_current_value()
        fig.set_size_inches(width / dpi, height / dpi)
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
                # cell + colorbar text follow the tick/frame colour
                tick_color = rgba_tuple_from_rgb_and_a(self.frame_color.get_current_value(), 255)
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
                cbar = fig.colorbar(ax.images[0], ax=ax, orientation="vertical")
                cbar.ax.tick_params(colors=tick_color)

                plt.xticks(range(len(item.df.columns)), item.df.columns)
                plt.yticks(range(len(item.df.index)), item.df.index)

                data = item.df
                # Adding annotations
                for i in range(len(data.index)):
                    for j in range(len(data.columns)):
                        if (
                            item.p is None
                            or item.p.iloc[i, j] < 0.05
                            or not item.config.only_significant.get_current_value()
                        ):
                            text = format_r_apa(data.iloc[i, j])  # + get_stars(item.p.iloc[i, j])

                            self._gc_ignore.append(
                                plt.text(
                                    j,
                                    i,
                                    text,
                                    ha="center",
                                    va="center",
                                    color=tick_color,
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

            if isinstance(item, Pie):
                bg = self.background_color.get_current_value()
                luminance = 0.299 * bg[0] + 0.587 * bg[1] + 0.114 * bg[2]
                text_color = (0, 0, 0) if luminance > 140 else (235, 235, 235)
                color_manager = Colors()
                slice_colors = [
                    rgba_tuple_from_rgb_and_a(color_manager.get_color_list(), 255) for _ in item.values
                ]
                ax.pie(
                    item.values,
                    labels=item.labels,
                    colors=slice_colors,
                    autopct="%1.1f%%",
                    startangle=90,
                    counterclock=False,
                    textprops={"color": rgba_tuple_from_rgb_and_a(text_color, 255)},
                    wedgeprops={"edgecolor": rgba_tuple_from_rgb_and_a(bg, 255), "linewidth": 1},
                )
                ax.set_aspect("equal")
                ax.axis("off")  # a pie needs no axes/frame

        # frame (spines + ticks): user-configurable color and thickness
        frame_color = rgba_tuple_from_rgb_and_a(self.frame_color.get_current_value(), 255)
        frame_thickness = self.frame_thickness.get_current_value()
        ax.tick_params(
            axis="both",
            which="major",
            labelsize=self.tick_label_font_size.get_current_value(),
            colors=frame_color,
            width=frame_thickness,
        )
        for side in ("top", "right", "left", "bottom"):
            ax.spines[side].set_color(frame_color)
            ax.spines[side].set_linewidth(frame_thickness)
        if not self.box_frame.get_current_value():
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

        # gridlines (behind the data)
        grid_mode = self.gridlines.get_current_value()
        if grid_mode != "None":
            grid_axis = {"Both": "both", "Horizontal": "y", "Vertical": "x"}.get(grid_mode, "both")
            ax.set_axisbelow(True)
            ax.grid(True, axis=grid_axis, color=frame_color, alpha=0.35, linewidth=max(0.5, frame_thickness * 0.6))

        if self.x_axis_items is not None:
            ax.set_xticks(range(len(self.x_axis_items)))
            ax.set_xticklabels(self.x_axis_items)

        ax.tick_params(axis="x", rotation=self.tilt_x_axis_labels.current_value)

        # axis titles -- placement follows the chosen layout (titles can be long)
        x_title = self.x_axis_title.get_current_value()
        y_title = self.y_axis_title.get_current_value()
        layout = self.axis_layout.get_current_value()
        if layout == "Edges":
            ax.set_xlabel(x_title, loc="right")
            ax.set_ylabel(y_title, loc="top")
        elif layout == "Flat Y":
            ax.set_xlabel(x_title, loc="right")
            # Horizontal y-title above the axis; precise left/top position is set after
            # tight_layout (so it can align to the left of the y tick labels).
            ax.set_ylabel(y_title, rotation=0, ha="left", va="bottom")
        else:  # Centered
            ax.set_xlabel(x_title)
            ax.set_ylabel(y_title)

        # Title colour auto-contrasts with the background (black on light, light on
        # dark) so titles stay readable on the Dark theme / dark backgrounds.
        bg = self.background_color.get_current_value()
        luminance = 0.299 * bg[0] + 0.587 * bg[1] + 0.114 * bg[2]
        title_color = (0, 0, 0) if luminance > 140 else (235, 235, 235)
        font_size = self.axis_title_font_size.get_current_value()
        for axis_label in (ax.xaxis.label, ax.yaxis.label):
            axis_label.set_fontsize(font_size)
            axis_label.set_fontname("Times New Roman")
            axis_label.set_color(rgba_tuple_from_rgb_and_a(title_color, 255))

        # set axis ranges
        if self.x_range is not None:
            ax.set_xlim(*self.x_range)
        if self.y_range is not None:
            ax.set_ylim(*self.y_range)

        if legend:
            leg = ax.legend(fontsize=self.legend_font_size.get_current_value())
            # Legend follows the background so it stays readable on dark themes.
            leg.get_frame().set_facecolor(rgba_tuple_from_rgb_and_a(face_color, max(bg_alpha, 200)))
            leg.get_frame().set_edgecolor(frame_color)
            for text in leg.get_texts():
                text.set_color(rgba_tuple_from_rgb_and_a(title_color, 255))

        fig.tight_layout()

        if layout == "Flat Y":
            self._place_flat_ylabel(fig, ax)

        return fig, ax

    @staticmethod
    def _place_flat_ylabel(fig, ax):
        """Position a horizontal (Flat Y) y-title at the top-left, aligned to the left
        edge of the y tick labels and lifted above the top spine so glyphs don't cross
        it. Measured after layout, in axes coordinates."""
        try:
            fig.canvas.draw()
            inv = ax.transAxes.inverted()
            left_edges = [
                inv.transform((t.get_window_extent().x0, 0))[0]
                for t in ax.get_yticklabels()
                if t.get_text()
            ]
            left_x = min(left_edges) if left_edges else -0.05
        except Exception:
            left_x = -0.05
        ax.yaxis.set_label_coords(left_x, 1.05)

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
        fig.savefig(buf, format="png", bbox_inches="tight", pad_inches=self.margin.get_current_value(), dpi=150)
        plt.close(fig)
        buf.seek(0)

        # 3) base64-encode the PNG bytes
        png_bytes = buf.getvalue()
        base64_png = base64.b64encode(png_bytes).decode("ascii")
        buf.close()

        # 4) title as editable text, then the image below (so it can be edited after
        # pasting into Word etc.)
        title = self.plot_title.get_current_value()
        title_html = f'<div class="double-spacing font"><b>{title}</b></div><br>\n' if title else ""
        html = f"""
        {title_html}<img src="data:image/png;base64,{base64_png}"
             alt="Plot Image"
             style="width:400px; height:auto;">
        """
        return html

    def get_svg_buffer(self):
        fig, _ = self.create_figure()
        buf = io.BytesIO()
        fig.savefig(buf, format="svg", bbox_inches="tight", pad_inches=self.margin.get_current_value())
        plt.close(fig)
        buf.seek(0)
        return buf

    def get_png_buffer(self):
        fig, _ = self.create_figure()
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", pad_inches=self.margin.get_current_value(), dpi=150)
        plt.close(fig)
        buf.seek(0)
        return buf

    def render_qimage(self, dpi=150):
        """Render directly to a QImage via a raster (PNG/Agg) buffer. Avoids the slow
        SVG serialize + QSvgRenderer parse round-trip used previously for on-screen
        display."""
        fig, _ = self.create_figure()
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight", pad_inches=self.margin.get_current_value(), dpi=dpi)
        plt.close(fig)
        image = QImage.fromData(buf.getvalue(), "PNG")
        buf.close()
        return image

    def copy_to_clipboard(self):
        buf = self.get_png_buffer()
        image = QImage.fromData(buf.getvalue(), "PNG")
        QApplication.clipboard().setImage(image)
        buf.close()
