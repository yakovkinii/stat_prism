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


"""Per-variable distribution + box plots split by group, shared by the t-test and ANOVA
result builders (which only differed in the element-name prefix)."""

import numpy as np
from scipy.stats import gaussian_kde

from src.common.qcolor import Colors
from src.common.translations import t
from src.side_area_panel.modules.common.result.plot_result import Bar, BarPlotConfig, Line, LinePlotConfig, PlotV2
from src.side_area_panel.modules.descriptive.plot import _histogram_edges, create_box_plot


def _parse_positive_float(text):
    try:
        value = float(text)
    except (TypeError, ValueError):
        return None
    return value if value > 0 else None


def _parse_float_or_none(text):
    try:
        return float(text)
    except (TypeError, ValueError):
        return None


def add_group_distribution_plots(
    result, df, selected_columns, numeric_columns, grouping_column, update, prefix, bin_width="", bin_reference=""
):
    """For each numeric variable, add a grouped histogram+KDE distribution plot and a box
    plot to `result`. `prefix` namespaces the element keys (e.g. 't_test' / 'anova'). The bins
    follow the user's width / reference (blank width defaults to (max - min) / 5 to one
    significant figure), matching the descriptive module."""
    width_value = _parse_positive_float(bin_width)
    reference_value = _parse_float_or_none(bin_reference)
    groupby_column = grouping_column
    groupby_values = df[groupby_column].drop_duplicates().values
    for idx, col in enumerate(selected_columns):
        update(10 + 80 * (idx + 1) / len(selected_columns))
        if col not in numeric_columns:
            continue

        plots = []
        n_items = len(groupby_values)

        # Drop NaNs in the value column explicitly before histogram/KDE
        col_series = df[col].dropna()
        if col_series.empty:
            continue
        x_all = _histogram_edges(col_series, width_value, reference_value)
        if x_all is None or len(x_all) < 2:
            continue
        x_vals = np.linspace(col_series.min(), col_series.max(), 500)

        # | g 1 g 2 g |
        bin_w = x_all[1] - x_all[0]
        width = bin_w * 0.9 / n_items
        gap = (bin_w - width * n_items) / (n_items + 1)
        centers = x_all[:-1] + bin_w / 2.0

        colors = Colors()

        for i, groupby_value in enumerate(groupby_values):
            df_subset = df.loc[df[groupby_column] == groupby_value]
            series = df_subset[col].dropna()
            if series.empty:
                continue
            kde = gaussian_kde(series)
            y_vals = kde(x_vals)
            color = colors.get_color_list()
            plots.append(
                Line(
                    x=x_vals,
                    y=y_vals,
                    label=f"{groupby_value}",
                    config=LinePlotConfig(color=color),
                    legend_string=f"{groupby_value}",
                )
            )

            # Offset of this group's dodged bar from the bin center. Count the group on bins
            # shifted by that offset so each bar is centered on the interval it was computed
            # from, rather than dodged away from the shared bin center.
            offset = -bin_w / 2.0 + gap + width / 2.0 + i * (width + gap)
            y, _ = np.histogram(series, bins=x_all + offset, density=True)
            plots.append(
                Bar(
                    x=centers + offset,
                    y=y,
                    width=width,
                    label=f"{groupby_value}",
                    config=BarPlotConfig(color=color),
                )
            )

        result.update_and_add_element(
            PlotV2(
                items=plots,
                title=t("ttest.plot.distribution_tab", col=col),
                plot_title=t("ttest.plot.distribution", col=col),
                x_axis_title=col,
                y_axis_title=t("ttest.plot.density"),
            ),
            f"{prefix} distribution_plot_{col}",
        )

        result.update_and_add_element(
            create_box_plot(
                groups=[df.loc[df[groupby_column] == groupby_value][col].dropna() for groupby_value in groupby_values],
                group_names=groupby_values,
                column=col,
                grouping_column=groupby_column,
            ),
            f"{prefix} box_plot_{col}",
        )
    return result
