#  Copyright (c) 2023 StatPrism Team. All rights reserved.

"""Per-variable distribution + box plots split by group, shared by the t-test and ANOVA
result builders (which only differed in the element-name prefix)."""

import numpy as np
from scipy.stats import gaussian_kde

from src.common.qcolor import Colors
from src.common.translations import t
from src.side_area_panel.modules.common.result.plot_result import Bar, BarPlotConfig, Line, LinePlotConfig, PlotV2
from src.side_area_panel.modules.descriptive.plot import create_box_plot


def add_group_distribution_plots(result, df, selected_columns, numeric_columns, grouping_column, update, prefix):
    """For each numeric variable, add a grouped histogram+KDE distribution plot and a box
    plot to `result`. `prefix` namespaces the element keys (e.g. 't_test' / 'anova')."""
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
        _, x_all = np.histogram(col_series, bins="auto", density=True)
        x_vals = np.linspace(col_series.min(), col_series.max(), 500)

        # | g 1 g 2 g |
        width = (x_all[1] - x_all[0]) * 0.9 / n_items if len(x_all) > 1 else 0.9 / max(n_items, 1)
        gap = ((x_all[1] - x_all[0]) - width * len(groupby_values)) / (len(groupby_values) + 1) if len(x_all) > 1 else 0

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

            y, x = np.histogram(series, bins=x_all, density=True)
            plots.append(
                Bar(
                    x=x[:-1] + gap + width / 2 + i * (width + gap) if len(x) > 1 else x,
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
