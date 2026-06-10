#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import logging

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import gaussian_kde

from src.common.constant import MDASH, ColumnType
from src.common.decorators import log_function
from src.common.qcolor import Colors
from src.data.data import Data
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.common.result.plot_result import (
    Bar,
    BarPlotConfig,
    Line,
    LinePlotConfig,
    PlotV2,
)
from src.side_area_panel.modules.descriptive.plot import create_box_plot
from src.side_area_panel.modules.descriptive.descriptive_result import DescriptiveResult
from src.side_area_panel.modules.descriptive.table import (
    get_descriptive_table_groupby,
    get_descriptive_table_no_groupby,
)


def calculate_descriptive_study_no_groupby(data: Data, result: DescriptiveResult):
    cfg = result.config
    selected_columns = cfg.column_selector[0]
    df = data.get_dataframe(
        columns=selected_columns,
    )

    numeric_columns = [col for col in selected_columns if data[col].column_type == ColumnType.NUMERIC]

    descriptive_results = []
    plot_result_elements = []
    for col in selected_columns:
        is_numeric = col in numeric_columns

        shapiro_wilk_w, shapiro_wilk_p = stats.shapiro(df[col].dropna()) if is_numeric else (MDASH, MDASH)

        descriptive_results.append(
            {
                "variable": col,
                "N": df[col].count(),
                "missing": df[col].isnull().sum(),
                "mean": round(df[col].mean(), 2) if is_numeric else MDASH,
                "std": round(df[col].std(), 2) if is_numeric else MDASH,
                "min": round(df[col].min(), 2) if is_numeric else MDASH,
                "max": round(df[col].max(), 2) if is_numeric else MDASH,
                "shapiro_wilk_w": shapiro_wilk_w,
                "shapiro_wilk_p": shapiro_wilk_p,
            }
        )

        if not is_numeric:
            continue

        # Histogram
        try:
            kde = gaussian_kde(df[col].dropna())
            x_vals = np.linspace(df[col].min(), df[col].max(), 500)
            y_vals = kde(x_vals)

            plot_line = Line(
                x=x_vals,
                y=y_vals,
                label=f"Distribution",
            )
        except Exception as e:
            logging.error(f"Error calculating KDE for column {col}: {e}")
            plot_line = None

        y, x = np.histogram(df[col], bins="auto", density=True)
        # bar plot
        plot_bar = Bar(
            x=x[:-1] + (x[1] - x[0]) / 2,
            y=y,
            width=0.9 * (x[1] - x[0]),
            label=f"Distribution",
        )

        plot_result = PlotV2(
            items=[plot_line, plot_bar] if plot_line else [plot_bar],
            title=f"Plot: Distribution of {col}",
            plot_title=f"Distribution of {col}",
            x_axis_title=col,
            y_axis_title="Density",
        )
        plot_result_elements.append(plot_result)

    descriptive_df = pd.DataFrame(descriptive_results)

    html_table = get_descriptive_table_no_groupby(descriptive_df, caption="Descriptive statistics")

    result.title_context = ", ".join([f"{col[:16]}" for col in selected_columns])
    result.result_elements = [html_table] + plot_result_elements
    return result


def calculate_descriptive_study_groupby(data: Data, result: DescriptiveResult):
    cfg = result.config
    selected_columns = cfg.column_selector[0]
    grouping_column = cfg.column_selector[1][0]
    df = data.get_dataframe(
        columns=selected_columns + [grouping_column],
    )
    groupby_column = grouping_column
    groupby_values = df[groupby_column].drop_duplicates().values

    numeric_columns = [col for col in selected_columns if data[col].column_type == ColumnType.NUMERIC]

    descriptive_results = []
    plot_result_elements = []
    for col in selected_columns:
        is_numeric = col in numeric_columns

        var_results = {}
        for groupby_value in groupby_values:
            df_subset = df.loc[df[groupby_column] == groupby_value]
            if not is_numeric or df_subset[col].count() < 3:
                shapiro_wilk_w, shapiro_wilk_p = MDASH, MDASH
            else:
                shapiro_wilk_w, shapiro_wilk_p = stats.shapiro(df_subset[col].dropna())

            var_results[groupby_value] = {
                "variable": col,
                "groupby": groupby_value,
                "N": df_subset[col].count(),
                "missing": df_subset[col].isnull().sum(),
                "mean": round(df_subset[col].mean(), 2) if is_numeric else MDASH,
                "std": round(df_subset[col].std(), 2) if is_numeric else MDASH,
                "min": round(df_subset[col].min(), 2) if is_numeric else MDASH,
                "max": round(df_subset[col].max(), 2) if is_numeric else MDASH,
                "shapiro_wilk_w": shapiro_wilk_w,
                "shapiro_wilk_p": shapiro_wilk_p,
            }
        descriptive_results.append(var_results)

        if not is_numeric:
            continue

        plots = []
        n_items = len(groupby_values)

        _, x_all = np.histogram(df[col], bins="auto", density=True)
        x_vals = np.linspace(df[col].min(), df[col].max(), 500)

        # | g 1 g 2 g |
        width = (x_all[1] - x_all[0]) * 0.9 / n_items
        gap = ((x_all[1] - x_all[0]) - width * len(groupby_values)) / (len(groupby_values) + 1)

        colors = Colors()

        for i, groupby_value in enumerate(groupby_values):
            df_subset = df.loc[df[groupby_column] == groupby_value]
            color = colors.get_color_list()
            try:
                kde = gaussian_kde(df_subset[col].dropna())
                y_vals = kde(x_vals)
                plot_line = Line(
                    x=x_vals,
                    y=y_vals,
                    label=f"{groupby_value}",
                    config=LinePlotConfig(color=color),
                    legend_string=f"{groupby_value}",
                )
                plots.append(plot_line)
            except Exception as e:
                logging.error(f"Error calculating KDE for column {col} and group {groupby_value}: {e}")

            y, x = np.histogram(df_subset[col], bins=x_all, density=True)
            bar_plot_config = BarPlotConfig(color=color)
            # bar plot # | g 1 g 2 g |
            plot_bar = Bar(
                x=x[:-1] + gap + width / 2 + i * (width + gap),
                y=y,
                width=width,
                label=f"{groupby_value}",
                config=bar_plot_config,
            )
            plots.append(plot_bar)

        plot_result = PlotV2(
            items=plots,
            title=f"Plot: Distribution of {col}",
            plot_title=f"Distribution of {col}",
            x_axis_title=col,
            y_axis_title="Density",
        )
        plot_result_elements.append(plot_result)

        box_plot_result = create_box_plot(
            groups=[df.loc[df[groupby_column] == groupby_value][col] for groupby_value in groupby_values],
            group_names=groupby_values,
            column=col,
            grouping_column=groupby_column,
        )

        plot_result_elements.append(box_plot_result)

    html_table = get_descriptive_table_groupby(
        descriptive_results,
        groupby_column=groupby_column,
        groupby_values=groupby_values,
        caption="Descriptive statistics",
    )

    result.title_context = ", ".join([f"{col[:16]}" for col in selected_columns]) + "\n" + f"{grouping_column[:16]}"
    result.result_elements = [html_table] + plot_result_elements
    return result


@log_function
def recalculate_descriptive_study(elements, result: DescriptiveResult) -> DescriptiveResult:
    data = DATA_MANAGER.get_data_from_data_label(
        data_label=result.config.data_source,
        current_result_id=result.unique_id,
    )

    grouping = result.config.column_selector[1]
    if not grouping:
        result = calculate_descriptive_study_no_groupby(data, result)
    else:
        result = calculate_descriptive_study_groupby(data, result)

    return result
