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

from src.common.constant import ColumnType
from src.common.qcolor import Colors
from src.common.translations import t
from src.side_area_panel.modules.common.result.plot_result import Bar, BarPlotConfig, Line, LinePlotConfig, PlotV2
from src.side_area_panel.modules.descriptive.plot import _histogram_edges, create_box_plot, ordinal_axis_tick_labels


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
    result,
    df,
    selected_columns,
    numeric_columns,
    grouping_column,
    update,
    prefix,
    bin_width="",
    bin_reference="",
    data=None,
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
        is_ordinal = data is not None and data[col].column_type == ColumnType.ORDINAL
        if col not in numeric_columns and not is_ordinal:
            continue
        # A true-ordinal column (kept ordinal -- not cast to numeric for a parametric method) is
        # plotted on its order codes with the axis relabelled to the face-value categories, so the
        # plot shows only face values, in the prescribed order, and works even for non-numeric labels.
        # A numeric column (including an ordinal cast to numeric) is plotted on its values as-is.
        is_true_ordinal = is_ordinal and col not in numeric_columns
        if is_true_ordinal:
            work = df.assign(**{col: df[col].map(data[col].order or {})})
            axis_tick_labels = ordinal_axis_tick_labels(data, col, work[col])
        else:
            work = df
            axis_tick_labels = None

        plots = []
        n_items = len(groupby_values)

        # Drop NaNs in the value column explicitly before histogram/KDE
        col_series = work[col].dropna()
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
            df_subset = work.loc[work[groupby_column] == groupby_value]
            series = df_subset[col].dropna()
            if series.empty:
                continue
            color = colors.get_color_list()
            # A group with a single value or no variation has no density curve (gaussian_kde needs a
            # non-singular covariance). Skip its line but keep the histogram bars, and note it so the
            # missing curve is not silently dropped.
            try:
                kde = gaussian_kde(series)
                y_vals = kde(x_vals)
                plots.append(
                    Line(
                        x=x_vals,
                        y=y_vals,
                        label=f"{groupby_value}",
                        config=LinePlotConfig(color=color),
                        legend_string=f"{groupby_value}",
                    )
                )
            except (np.linalg.LinAlgError, ValueError):
                result.set_warning(t("ttest.warning.kde_failed", col=col))

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
                x_axis_tick_labels=axis_tick_labels,
            ),
            f"{prefix} distribution_plot_{col}",
        )

        result.update_and_add_element(
            create_box_plot(
                groups=[work.loc[work[groupby_column] == groupby_value][col].dropna() for groupby_value in groupby_values],
                group_names=groupby_values,
                column=col,
                grouping_column=groupby_column,
                y_axis_tick_labels=axis_tick_labels,
            ),
            f"{prefix} box_plot_{col}",
        )
    return result
