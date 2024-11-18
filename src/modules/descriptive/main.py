#
#  Copyright (c) 2024 Ivan I. Yakovkin. All rights reserved.
#

import logging

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import gaussian_kde

from src.common.constant import MDASH, ColumnType
from src.common.decorators import log_function
from src.common.result.classes.html_result import HTMLResultElement
from src.common.result.classes.plot_result import Bar, BarPlotConfig, Colors, Line, LinePlotConfig, PlotResultElement
from src.modules.descriptive.plot import create_box_plot
from src.modules.descriptive.result import DescriptiveResult, DescriptiveStudyConfig
from src.modules.descriptive.table import get_descriptive_table_groupby, get_descriptive_table_no_groupby
from src.settings_panel.panels.registry import PanelRegistry


def calculate_descriptive_study_no_groupby(df, config, result):
    numeric_columns = [
        col
        for col, col_type in zip(config.selected_columns, config.selected_columns_types)
        if col_type == ColumnType.NUMERIC
    ]

    descriptive_results = []
    plot_result_elements = []
    for col in config.selected_columns:
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

        kde = gaussian_kde(df[col].dropna())
        x_vals = np.linspace(df[col].min(), df[col].max(), 500)
        y_vals = kde(x_vals)

        plot_line = Line(
            x=x_vals,
            y=y_vals,
            label=f"Distribution",
        )

        y, x = np.histogram(df[col], bins="auto", density=True)
        # bar plot
        plot_bar = Bar(
            x=x[:-1] + (x[1] - x[0]) / 2,
            y=y,
            width=0.9 * (x[1] - x[0]),
            label=f"Distribution",
        )

        plot_result = PlotResultElement(
            settings_panel_index=PanelRegistry.PLOT_RESULT_ITEM_SETTINGS.settings_stacked_widget_index,
            tab_title=f"Plot: Distribution of {col}",
            plot_title=f"Distribution of {col}",
            x_axis_title=col,
            y_axis_title="Density",
        )
        plot_result.items = [plot_line, plot_bar]
        plot_result_elements.append(plot_result)

    descriptive_df = pd.DataFrame(descriptive_results)

    html_table = get_descriptive_table_no_groupby(descriptive_df, caption="Descriptive statistics")
    html_result_element = HTMLResultElement(
        settings_panel_index=PanelRegistry.HTML_RESULT_ITEM_SETTINGS.settings_stacked_widget_index
    )

    html_result_element.items.append(html_table)
    html_result_element.set_table_id("1")
    html_result_element.table_caption = html_table.table_caption

    result.title_context = ", ".join([f"{col[:16]}" for col in config.selected_columns])
    result.result_elements = [html_result_element] + plot_result_elements
    return result


def calculate_descriptive_study_groupby(df, config, result):
    groupby_column = config.grouping_column
    groupby_values = df[groupby_column].drop_duplicates().values

    numeric_columns = [
        col
        for col, col_type in zip(config.selected_columns, config.selected_columns_types)
        if col_type == ColumnType.NUMERIC
    ]

    descriptive_results = []
    plot_result_elements = []
    for col in config.selected_columns:
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
            kde = gaussian_kde(df_subset[col].dropna())
            y_vals = kde(x_vals)
            color = colors.get_color_list()
            line_plot_config = LinePlotConfig(color=color)
            plot_line = Line(
                x=x_vals,
                y=y_vals,
                label=f"{groupby_value}",
                config=line_plot_config,
                legend_string=f"{groupby_value}",
            )
            plots.append(plot_line)

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

        plot_result = PlotResultElement(
            settings_panel_index=PanelRegistry.PLOT_RESULT_ITEM_SETTINGS.settings_stacked_widget_index,
            tab_title=f"Plot: Distribution of {col}",
            plot_title=f"Distribution of {col}",
            x_axis_title=col,
            y_axis_title="Density",
        )
        plot_result.items = plots
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
    html_result_element = HTMLResultElement(
        settings_panel_index=PanelRegistry.HTML_RESULT_ITEM_SETTINGS.settings_stacked_widget_index
    )

    html_result_element.items.append(html_table)
    html_result_element.set_table_id("1")
    html_result_element.table_caption = html_table.table_caption

    result.title_context = (
        ", ".join([f"{col[:16]}" for col in config.selected_columns]) + "\n" + f"{config.grouping_column[:16]}"
        if config.grouping_column is not None
        else ""
    )
    result.result_elements = [html_result_element] + plot_result_elements
    return result


@log_function
def recalculate_descriptive_study(df: pd.DataFrame, result: DescriptiveResult) -> DescriptiveResult:
    config: DescriptiveStudyConfig = result.config

    if len(config.selected_columns) < 1:
        msg = "Please select one Grouping Column and at least one Variable"
        result.set_placeholder(msg)
        logging.debug(msg)
        return result

    if len(config.filters) > 0:
        for filter_settings in config.filters:
            query = filter_settings.get_query()
            logging.debug(f"Applying Filter: {query}")
            df = df.query(query)
    else:
        logging.debug("No filter applied")

    df = (
        df[config.selected_columns + [config.grouping_column]]
        if config.grouping_column
        else df[config.selected_columns]
    )

    if config.grouping_column is None:
        result = calculate_descriptive_study_no_groupby(df, config, result)
    else:
        result = calculate_descriptive_study_groupby(df, config, result)

    return result
