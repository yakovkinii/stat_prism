import logging
from typing import Dict, Union

import numpy as np
import pandas as pd

from src.common.decorators import log_function
from src.common.result.classes.html_result import Cell, HTMLResultElement, HTMLTable, Row
from src.common.utility import format_statistic_apa
from src.modules.correlation.binary_correlations import phi_correlation_table, tetrachoric_corr_matrix
from src.modules.correlation.result import CorrelationType
from src.modules.reliability.result import ReliabilityResult, ReliabilityStudyConfig
from src.settings_panel.panels.registry import PanelRegistry


@log_function
def recalculate_reliability_study(
    df: pd.DataFrame, result: ReliabilityResult, ordinal_orders: Dict[str, Dict[Union[int, float, str], int]]
) -> ReliabilityResult:
    config: ReliabilityStudyConfig = result.config

    if len(config.selected_columns) < 2:
        msg = "Please select at least two questions"
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

    df = df[config.selected_columns].copy()

    # map ordinal columns
    for col in config.selected_columns:
        if col in ordinal_orders:
            df[col] = df[col].map(ordinal_orders[col])

    correlation_type_map = {
        CorrelationType.PEARSON: "pearson",
        CorrelationType.SPEARMAN: "spearman",
        CorrelationType.KENDALL: "kendall",
    }

    if config.correlation_type in correlation_type_map.keys():
        correlation_matrix = df.corr(method=correlation_type_map[config.correlation_type])
        alpha = cronbach_alpha(correlation_matrix.values)
    else:
        # Check if all columns have most 2 unique values
        if not all(df[col].nunique() <= 2 for col in df.columns):
            msg = "All columns must have at most 2 unique values for the selected correlation type"
            result.set_placeholder(msg)
            logging.debug(msg)
            return result
        # Scale all columns to 0..1
        for col in df.columns:
            df[col] = df[col] - df[col].min()
            if df[col].max() != 0:
                df[col] = df[col] / df[col].max()

        if config.correlation_type == CorrelationType.PHI:
            correlation_matrix = phi_correlation_table(df)
        else:
            correlation_matrix = tetrachoric_corr_matrix(df)[0]

        alpha = cronbach_alpha(correlation_matrix.values)

    table = HTMLTable([])
    table.table_caption = "Cronbach's Alpha"
    table.add_title_row_apa(
        Row(
            [
                Cell(),
                Cell("Cronbach's Alpha", center=True),
            ]
        )
    )

    table.add_single_row_apa(
        Row(
            [
                Cell(config.scale_column if config.scale_column is not None else "", push_to_left=True),
                Cell(format_statistic_apa(alpha), center=True),
            ]
        )
    )

    html_result_element = HTMLResultElement(
        settings_panel_index=PanelRegistry.HTML_RESULT_ITEM_SETTINGS.settings_stacked_widget_index
    )
    html_result_element.items = [table]
    result.result_elements = [html_result_element]

    return result


def cronbach_alpha(corr_matrix: np.ndarray) -> float:
    k = corr_matrix.shape[0]
    trace = np.trace(corr_matrix)
    matrix_sum = np.sum(corr_matrix)
    alpha = (k / (k - 1)) * (1 - (trace / matrix_sum))
    return alpha
