#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from typing import List

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import gaussian_kde

from src.common.qcolor import Colors
from src.common.translations import t
from src.side_area_panel.modules.common.result.plot_result import (
    Bar,
    BarPlotConfig,
    Box,
    Line,
    LinePlotConfig,
    Pie,
    PlotV2,
    Scatter,
    ScatterPlotConfig,
)


def create_box_plot(
    groups: List[pd.Series],
    group_names: List[str],
    column: str,
    grouping_column: str,
) -> PlotV2:
    """Grouped box plot (shared with the mean-comparison module)."""
    items = []
    colors = Colors()
    for i, (group, group_name) in enumerate(zip(groups, group_names)):
        color = colors.get_color_list()
        items.append(Box.from_data(group, index=i, label=group_name, color=color))

    plot_result = PlotV2(
        items=items,
        title=f"Box Plot: Comparison of {column} within {grouping_column}",
        plot_title=f"Comparison of {column} within {grouping_column}",
        x_axis_title=grouping_column,
        y_axis_title=column,
        x_axis_items=group_names,
    )
    return plot_result


def _histogram_edges(series: pd.Series, bin_width):
    """Histogram bin edges for a series. `bin_width` None/<=0 -> automatic; otherwise a
    fixed width with edges centred so each multiple of the width is a bar centre (so
    Likert 1..7 with width 1 gives one bar per value)."""
    data = series.dropna()
    if data.empty:
        return None
    if bin_width and bin_width > 0:
        start = data.min() - bin_width / 2.0
        stop = data.max() + bin_width
        return np.arange(start, stop, bin_width)
    _, edges = np.histogram(data, bins="auto")
    return edges


def _kde_curve(series: pd.Series, edges, kde_smoothing):
    data = series.dropna()
    if len(data) < 2 or data.nunique() < 2:
        return None, None
    try:
        kde = gaussian_kde(data)
        if kde_smoothing and kde_smoothing > 0:
            kde.set_bandwidth(kde.factor * kde_smoothing)
        x = np.linspace(edges[0], edges[-1], 500)
        return x, kde(x)
    except Exception:
        return None, None


def make_distribution_plot(df, col, groupby_column, groupby_values, bin_width, kde_smoothing, show_kde):
    """Histogram (density) + optional KDE; overlaid per group when grouping is set."""
    edges = _histogram_edges(df[col], bin_width)
    if edges is None or len(edges) < 2:
        return None

    items = []
    colors = Colors()
    bin_w = edges[1] - edges[0]

    if groupby_column is None:
        color = colors.get_color_list()
        if show_kde:
            x, y = _kde_curve(df[col], edges, kde_smoothing)
            if x is not None:
                items.append(Line(x=x, y=y, label="Distribution", config=LinePlotConfig(color=color)))
        counts, _ = np.histogram(df[col].dropna(), bins=edges, density=True)
        items.append(
            Bar(
                x=edges[:-1] + bin_w / 2.0,
                y=counts,
                width=0.9 * bin_w,
                label="Distribution",
                config=BarPlotConfig(color=color),
            )
        )
    else:
        n_items = len(groupby_values)
        width = bin_w * 0.9 / n_items
        gap = (bin_w - width * n_items) / (n_items + 1)
        for i, groupby_value in enumerate(groupby_values):
            subset = df.loc[df[groupby_column] == groupby_value]
            color = colors.get_color_list()
            if show_kde:
                x, y = _kde_curve(subset[col], edges, kde_smoothing)
                if x is not None:
                    items.append(
                        Line(
                            x=x,
                            y=y,
                            label=str(groupby_value),
                            config=LinePlotConfig(color=color),
                            legend_string=str(groupby_value),
                        )
                    )
            counts, _ = np.histogram(subset[col].dropna(), bins=edges, density=True)
            items.append(
                Bar(
                    x=edges[:-1] + gap + width / 2.0 + i * (width + gap),
                    y=counts,
                    width=width,
                    label=str(groupby_value),
                    config=BarPlotConfig(color=color),
                )
            )

    if not items:
        return None
    title = t("descriptive.plot.distribution", col=col)
    return PlotV2(
        items=items,
        title=title,
        plot_title=title,
        x_axis_title=col,
        y_axis_title=t("descriptive.density"),
    )


def make_box_plot(df, col, groupby_column, groupby_values):
    """Box plot with outliers; one box (whole variable) or one per group."""
    items = []
    colors = Colors()
    if groupby_column is None:
        data = df[col].dropna()
        if data.empty:
            return None
        items.append(Box.from_data(data, index=0, label=col, color=colors.get_color_list()))
        x_axis_items = [col]
        x_axis_title = ""
    else:
        x_axis_items = []
        for i, groupby_value in enumerate(groupby_values):
            data = df.loc[df[groupby_column] == groupby_value][col].dropna()
            if data.empty:
                continue
            items.append(Box.from_data(data, index=i, label=str(groupby_value), color=colors.get_color_list()))
            x_axis_items.append(str(groupby_value))
        x_axis_title = groupby_column

    if not items:
        return None
    title = t("descriptive.plot.box", col=col)
    return PlotV2(
        items=items,
        title=title,
        plot_title=title,
        x_axis_title=x_axis_title,
        y_axis_title=col,
        x_axis_items=x_axis_items,
    )


def make_qq_plot(series: pd.Series, col: str):
    """Normal Q-Q plot: sample quantiles vs theoretical normal quantiles + a fit line."""
    data = series.dropna()
    if len(data) < 3:
        return None
    (osm, osr), (slope, intercept, _) = stats.probplot(data, dist="norm")
    colors = Colors()
    scatter = Scatter(x=osm, y=osr, label="Q-Q points", config=ScatterPlotConfig(color=colors.get_color_list()))
    line_x = np.array([osm.min(), osm.max()])
    line = Line(
        x=line_x,
        y=intercept + slope * line_x,
        label="Reference line",
        config=LinePlotConfig(color=colors.get_color_list()),
    )
    title = t("descriptive.plot.qq", col=col)
    return PlotV2(
        items=[scatter, line],
        title=title,
        plot_title=title,
        x_axis_title=t("descriptive.qq.theoretical"),
        y_axis_title=t("descriptive.qq.sample"),
    )


def make_frequency_bar_plot(series: pd.Series, col: str):
    """Counts per category for a categorical variable (whole variable)."""
    value_counts = series.value_counts().sort_index()
    if value_counts.empty:
        return None
    categories = [str(c) for c in value_counts.index]
    bar = Bar(
        x=np.arange(len(categories)),
        y=value_counts.values,
        width=0.8,
        label="Frequency",
        config=BarPlotConfig(color=Colors().get_color_list()),
    )
    title = t("descriptive.plot.frequency", col=col)
    return PlotV2(
        items=[bar],
        title=title,
        plot_title=title,
        x_axis_title=col,
        y_axis_title=t("descriptive.freq.count"),
        x_axis_items=categories,
    )


def make_pie_plot(series: pd.Series, col: str):
    """Category-share pie for a categorical variable (whole variable)."""
    value_counts = series.value_counts().sort_index()
    if value_counts.empty:
        return None
    title = t("descriptive.plot.pie", col=col)
    return PlotV2(
        items=[
            Pie(
                labels=[str(c) for c in value_counts.index],
                values=list(value_counts.values),
                label="Pie",
            )
        ],
        title=title,
        plot_title=title,
        x_axis_title="",
        y_axis_title="",
    )
