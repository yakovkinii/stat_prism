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
from src.side_area_panel.modules.common.utility import format_value_apa, smart_comma_join


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


def _histogram_edges(series: pd.Series, bin_width, bin_reference=None):
    """Histogram bin edges for a series. `bin_width` None/<=0 -> automatic. Otherwise a
    fixed width; `bin_reference` (if given) is the centre of one bin, so the bars align to
    it (e.g. reference 0 + width 1 centres a bar on every integer). With no reference the
    bins are centred on the data minimum (so Likert 1..7 with width 1 gives one bar per
    value)."""
    data = series.dropna()
    if data.empty:
        return None
    if bin_width and bin_width > 0:
        w = bin_width
        if bin_reference is not None:
            k_start = int(np.floor((data.min() - bin_reference) / w))
            k_end = int(np.ceil((data.max() - bin_reference) / w))
            centers = bin_reference + np.arange(k_start, k_end + 1) * w
            return np.append(centers - w / 2.0, centers[-1] + w / 2.0)
        start = data.min() - w / 2.0
        stop = data.max() + w
        return np.arange(start, stop, w)
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


def make_distribution_plot(
    df, col, groupby_column, groupby_values, bin_width, bin_reference, kde_smoothing, show_kde
):
    """Histogram (density) + optional KDE; overlaid per group when grouping is set."""
    edges = _histogram_edges(df[col], bin_width, bin_reference)
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


def _outliers(subframe, col, id_column):
    """Return Tukey outliers as a list of (value, label) where label is the row's ID
    (when an id_column is given) or the formatted value."""
    values = subframe[col].dropna()
    if values.empty:
        return []
    q1, q3 = values.quantile(0.25), values.quantile(0.75)
    iqr = q3 - q1
    low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    labels = []
    for index, value in values[(values < low) | (values > high)].items():
        label = str(subframe.loc[index, id_column]) if id_column is not None else format_value_apa(value, 2)
        labels.append((value, label))
    return labels


def make_box_plot(df, col, groupby_column, groupby_values, id_column=None, mark_outliers=False):
    """Box plot with outliers; one box (whole variable) or one per group. Outliers are
    listed beneath the plot and optionally labelled on it."""
    items = []
    colors = Colors()
    outlier_sentences = []

    if groupby_column is None:
        boxes_data = [(col, df)]
    else:
        boxes_data = [(str(gv), df.loc[df[groupby_column] == gv]) for gv in groupby_values]

    x_axis_items = []
    for label, subframe in boxes_data:
        values = subframe[col].dropna()
        if values.empty:
            continue
        position = len(items)  # contiguous positions so boxes align with the tick labels
        box = Box.from_data(values, index=position, label=label, color=colors.get_color_list())
        outliers = _outliers(subframe, col, id_column)
        if outliers:
            if mark_outliers:
                box.outlier_labels = outliers
            listed = smart_comma_join(
                [
                    f"{lab} ({format_value_apa(val, 2)})" if id_column is not None else lab
                    for val, lab in outliers
                ]
            )
            outlier_sentences.append(
                t("descriptive.outliers.line", target=label, n=len(outliers), items=listed)
            )
        items.append(box)
        x_axis_items.append(label)

    if not items:
        return None, None

    title = t("descriptive.plot.box", col=col)
    plot = PlotV2(
        items=items,
        title=title,
        plot_title=title,
        x_axis_title=(groupby_column if groupby_column else ""),
        y_axis_title=col,
        x_axis_items=x_axis_items,
    )
    outlier_text = " ".join(outlier_sentences) if outlier_sentences else None
    return plot, outlier_text


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
