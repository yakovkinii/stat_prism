#  Copyright (C) 2023-2026  StatPrism Team
#  Balashevych A. K., Petrova N. V., Yakovkin I. I.
#
#  This file is part of StatPrism.
#
#  StatPrism is free software: you can redistribute it and/or modify it under
#  the terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  StatPrism is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with
#  StatPrism.  If not, see <https://www.gnu.org/licenses/>.


from typing import List

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import gaussian_kde

from src.common.constant import ID_COLUMN_NAME
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
from src.side_area_panel.modules.common.utility import round_to_one_sig_fig


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
    """Histogram bin edges for a series. A blank width defaults to (max - min) / 5 rounded to
    one significant figure; a blank reference defaults to 0. The reference is the center of one
    bin, so the bars align to it (e.g. reference 0 + width 1 centers a bar on every integer)."""
    data = series.dropna()
    if data.empty:
        return None
    lo, hi = float(data.min()), float(data.max())
    if bin_width and bin_width > 0:
        w = bin_width
    else:
        span = hi - lo
        w = round_to_one_sig_fig(span / 5.0) if span > 0 else 0
        if w <= 0:  # constant column (or degenerate span) -> fall back to automatic bins
            _, edges = np.histogram(data, bins="auto")
            return edges
    reference = bin_reference if bin_reference is not None else 0.0
    k_start = int(np.floor((lo - reference) / w))
    k_end = int(np.ceil((hi - reference) / w))
    centers = reference + np.arange(k_start, k_end + 1) * w
    return np.append(centers - w / 2.0, centers[-1] + w / 2.0)


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


def make_distribution_plot(df, col, groupby_column, groupby_values, bin_width, bin_reference, kde_smoothing, show_kde):
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
        centers = edges[:-1] + bin_w / 2.0
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
            # Offset of this group's dodged bar from the bin center. Count the group on bins
            # shifted by that offset so each bar is centered on the interval it was computed
            # from, rather than dodged away from the shared bin center.
            offset = -bin_w / 2.0 + gap + width / 2.0 + i * (width + gap)
            counts, _ = np.histogram(subset[col].dropna(), bins=edges + offset, density=True)
            items.append(
                Bar(
                    x=centers + offset,
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


def _outliers(subframe, col):
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
        label = str(subframe.loc[index, ID_COLUMN_NAME])
        labels.append((value, label))
    return labels


def make_box_plot(df, col, groupby_column, groupby_values, id_column=None, mark_outliers=False):
    """Box plot; one box (whole variable) or one per group. Outliers are optionally
    labelled on the plot (the verbal outlier report lives under the summary table)."""
    items = []
    colors = Colors()

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
        if mark_outliers:
            outliers = _outliers(subframe, col)
            if outliers:
                box.outlier_labels = outliers
        items.append(box)
        x_axis_items.append(label)

    if not items:
        return None

    title = t("descriptive.plot.box", col=col)
    return PlotV2(
        items=items,
        title=title,
        plot_title=title,
        x_axis_title=(groupby_column if groupby_column else ""),
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


def make_frequency_bar_plot(df, col: str, groupby_column=None, groupby_values=None, category_order=None):
    """Counts per category. One bar per category for the whole variable, or grouped
    side-by-side bars (one colour + legend entry per group) when grouping is set.
    `category_order` (if given) sets the category display order, e.g. ordinality."""
    colors = Colors()
    title = t("descriptive.plot.frequency", col=col)

    if groupby_column is None:
        value_counts = df[col].value_counts()
        if value_counts.empty:
            return None
        if category_order is not None:
            value_counts = value_counts.reindex(category_order)
        else:
            value_counts = value_counts.sort_index()
        categories = [str(c) for c in value_counts.index]
        items = [
            Bar(
                x=np.arange(len(categories)),
                y=value_counts.values,
                width=0.8,
                label="Frequency",
                config=BarPlotConfig(color=colors.get_color_list()),
            )
        ]
    else:
        all_categories = category_order if category_order is not None else sorted(df[col].dropna().unique(), key=str)
        if len(all_categories) == 0:
            return None
        categories = [str(c) for c in all_categories]
        n_groups = len(groupby_values)
        width = 0.8 / n_groups
        items = []
        for i, groupby_value in enumerate(groupby_values):
            counts = df.loc[df[groupby_column] == groupby_value, col].value_counts()
            y = [int(counts.get(category, 0)) for category in all_categories]
            x = np.arange(len(all_categories)) - 0.4 + width / 2.0 + i * width
            items.append(
                Bar(
                    x=x,
                    y=y,
                    width=width,
                    label=str(groupby_value),
                    legend_string=str(groupby_value),
                    config=BarPlotConfig(color=colors.get_color_list()),
                )
            )

    return PlotV2(
        items=items,
        title=title,
        plot_title=title,
        x_axis_title=col,
        y_axis_title=t("descriptive.freq.count"),
        x_axis_items=categories,
    )


def make_pie_plot(series: pd.Series, col: str, category_order=None):
    """Category-share pie for a categorical variable (whole variable). `category_order`
    (if given) sets the slice display order, e.g. ordinality."""
    value_counts = series.value_counts()
    if value_counts.empty:
        return None
    if category_order is not None:
        value_counts = value_counts.reindex(category_order)
    else:
        value_counts = value_counts.sort_index()
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
