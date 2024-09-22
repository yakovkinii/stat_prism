import logging

import numpy as np
import pandas as pd
from PySide6.QtWidgets import QMessageBox
from scipy import stats
from scipy.stats import gaussian_kde

from src.common.constant import MDASH
from src.common.result.classes.html_result import HTMLResultElement
from src.common.result.classes.plot_result import Bar, Line, PlotResultElement
from src.modules.descriptive.result import DescriptiveResult, DescriptiveStudyConfig
from src.modules.descriptive.table import get_descriptive_table_no_groupby
from src.settings_panel.panels.registry import PanelRegistry


def calculate_descriptive_study_no_groupby(df, config, result):
    descriptive_results = []
    plot_result_elements = {}
    for col in config.selected_columns1:
        is_numeric = pd.api.types.is_numeric_dtype(df[col])

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

        kde = gaussian_kde(df[col].dropna())
        x_vals = np.linspace(df[col].min(), df[col].max(), 500)
        y_vals = kde(x_vals)

        plot_line = Line(
            x=x_vals,
            y=y_vals,
            label=f"Line: Distribution",
        )

        y, x = np.histogram(df[col], bins="auto", density=True)
        # bar plot
        plot_bar = Bar(
            x=x[:-1] + (x[1] - x[0]) / 2,
            y=y,
            width=0.9 * (x[1] - x[0]),
            label=f"Bar: Distribution",
        )

        plot_result = PlotResultElement(
            settings_panel_index=PanelRegistry.PLOT_RESULT_ITEM_SETTINGS.settings_stacked_widget_index,
            tab_title=f"Plot: Distribution of {col}",
            plot_title=f"Distribution of {col}",
            x_axis_title=col,
            y_axis_title="Density",
        )
        plot_result.items = [plot_line, plot_bar]
        name = f"{col}"
        while name in plot_result_elements:
            name += "_"
        plot_result_elements[name] = plot_result

    descriptive_df = pd.DataFrame(descriptive_results)

    html_table = get_descriptive_table_no_groupby(descriptive_df, caption="Descriptive statistics")
    html_result_element = HTMLResultElement(
        settings_panel_index=PanelRegistry.HTML_RESULT_ITEM_SETTINGS.settings_stacked_widget_index
    )

    html_result_element.items.append(html_table)
    html_result_element.set_table_id("1")
    html_result_element.table_caption = html_table.table_caption

    result.title_context = (
        ", ".join([f"{col[:16]}" for col in config.selected_columns1])
        + "\n"
        + ", ".join([f"{col[:16]}" for col in config.selected_columns2])
    )
    result.set_elements(html_result_element, plot_result_elements)
    return result


def calculate_descriptive_study_groupby(df, config, result):
    message = "Descriptive with groupby is not implemented yet"
    logging.info(message)
    QMessageBox.warning(None, "Warning", message)

    # grouped = df.groupby(config.selected_columns2)
    #
    # if len(grouped) != 2:
    #     result.set_placeholder()
    #     logging.info("T-test requires exactly two groups")
    #     return result
    #
    # # Initialize a dictionary to store the t-test results
    # t_test_results = []
    #
    # group_names = [name[0] for name, group in grouped]
    #
    # # Perform t-test for each column in selected_columns1
    # for col in config.selected_columns1:
    #     # Get the data for each group
    #     group_data = [group[col].dropna().values for name, group in grouped]
    #     t_test_result = stats.ttest_ind(group_data[0], group_data[1])
    #     t_stat, p_val, deg_free = t_test_result.statistic, t_test_result.pvalue, t_test_result.df
    #     mean, std = [group.mean() for group in group_data], [group.std() for group in group_data]
    #     t_test_results.append(
    #         {
    #             "variable": col,
    #             "mean1": mean[0],
    #             "std1": std[0],
    #             "mean2": mean[1],
    #             "std2": std[1],
    #             "t-statistic": t_stat,
    #             "p-value": p_val,
    #             "df": deg_free,
    #         }
    #     )
    # t_test_df = pd.DataFrame(t_test_results)
    #
    # html_table = get_t_test_table(t_test_df, group_names, caption="T-test results")
    # html_result_element = HTMLResultElement(
    #     settings_panel_index=PanelRegistry.HTML_RESULT_ITEM_SETTINGS.settings_stacked_widget_index
    # )
    #
    # html_result_element.items.append(html_table)
    # html_result_element.set_table_id("1")
    # html_result_element.table_caption = html_table.table_caption
    #
    # result.title_context = (
    #         ", ".join([f"{col[:16]}" for col in config.selected_columns1])
    #         + "\n"
    #         + ", ".join([f"{col[:16]}" for col in config.selected_columns2])
    # )
    # result.set_elements(html_result_element, {})

    return result


def recalculate_descriptive_study(df: pd.DataFrame, result: DescriptiveResult) -> DescriptiveResult:
    logging.info("Recalculating correlation study")

    config: DescriptiveStudyConfig = result.config
    if len(config.selected_columns1) < 1:
        result.set_placeholder()
        logging.info("Not enough columns selected")
        return result

    if len(config.filters) > 0:
        for filter_settings in config.filters:
            df = df.query(filter_settings.get_query())
    else:
        logging.info("No filter applied")

    df = df[config.selected_columns1 + config.selected_columns2]

    if len(config.selected_columns2) == 0:
        result = calculate_descriptive_study_no_groupby(df, config, result)
    else:
        result = calculate_descriptive_study_groupby(df, config, result)

    return result
