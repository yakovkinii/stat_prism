import logging

import pandas as pd
from scipy.stats import stats

from src.common.result.classes.html_result import HTMLResultElement
from src.modules.t_test.result import TTestResult, TTestStudyConfig
from src.modules.t_test.table import get_t_test_table
from src.settings_panel.panels.registry import PanelRegistry


def recalculate_t_test_study(df: pd.DataFrame, result: TTestResult) -> TTestResult:
    logging.info("Recalculating correlation study")

    config: TTestStudyConfig = result.config
    if len(config.selected_columns1) < 1 or len(config.selected_columns2) < 1:
        result.set_placeholder()
        logging.info("Not enough columns selected")
        return result

    if len(config.filters) > 0:
        for filter_settings in config.filters:
            df = df.query(filter_settings.get_query())
    else:
        logging.info("No filter applied")

    df = df[config.selected_columns1 + config.selected_columns2]

    grouped = df.groupby(config.selected_columns2)

    if len(grouped) != 2:
        result.set_placeholder()
        logging.info("T-test requires exactly two groups")
        return result

    # Initialize a dictionary to store the t-test results
    t_test_results = []

    group_names = [name[0] for name, group in grouped]

    # Perform t-test for each column in selected_columns1
    for col in config.selected_columns1:
        # Get the data for each group
        group_data = [group[col].dropna().values for name, group in grouped]
        t_test_result = stats.ttest_ind(group_data[0], group_data[1])
        t_stat, p_val, deg_free = t_test_result.statistic, t_test_result.pvalue, t_test_result.df
        mean, std = [group.mean() for group in group_data], [group.std() for group in group_data]
        t_test_results.append(
            {
                "variable": col,
                "mean1": mean[0],
                "std1": std[0],
                "mean2": mean[1],
                "std2": std[1],
                "t-statistic": t_stat,
                "p-value": p_val,
                "df": deg_free,
            }
        )
    t_test_df = pd.DataFrame(t_test_results)

    html_table = get_t_test_table(t_test_df, group_names, caption="T-test results")
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
    result.set_elements(html_result_element, {})
    return result
