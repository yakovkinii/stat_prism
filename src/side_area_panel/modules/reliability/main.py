#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import logging

import numpy as np

from src.common.decorators import log_function
from src.data.data import Data
from src.side_area_panel.modules.common.mathematics.correlation.binary_correlations import (
    phi_correlation_table,
    tetrachoric_corr_matrix,
)
from src.side_area_panel.modules.common.result.html_result import Cell, HTMLTableV2, Row
from src.side_area_panel.modules.common.utility import format_statistic_apa
from src.side_area_panel.modules.correlation.result import CorrelationType
from src.side_area_panel.modules.reliability.result import (
    ReliabilityResult,
    ReliabilityStudyConfig,
)


@log_function
def recalculate_reliability_study(data: Data, result: ReliabilityResult) -> ReliabilityResult:
    config: ReliabilityStudyConfig = result.config

    df = data.get_dataframe(filters=result.config.filters, columns=result.config.selected_columns, map_ordinal=True)

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

    table = HTMLTableV2(table_caption="Cronbach's Alpha")
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

    result.result_elements = [table]

    return result


def cronbach_alpha(corr_matrix: np.ndarray) -> float:
    k = corr_matrix.shape[0]
    trace = np.trace(corr_matrix)
    matrix_sum = np.sum(corr_matrix)
    alpha = (k / (k - 1)) * (1 - (trace / matrix_sum))
    return alpha
