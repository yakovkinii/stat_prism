#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import logging

import numpy as np

from src.common.decorators import log_function
from src.common.translations import t
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.common.mathematics.correlation.binary_correlations import (
    phi_correlation_table,
    tetrachoric_corr_matrix,
)
from src.side_area_panel.modules.common.result.html_result import Cell, HTMLTableV2, Row
from src.side_area_panel.modules.common.utility import format_statistic_apa
from src.side_area_panel.modules.correlation.result import (
    CORRELATION_TYPE_MAP,
    CorrelationType,
)
from src.side_area_panel.modules.reliability.result import (
    ReliabilityResult,
    ReliabilityStudyConfig,
)


@log_function
def recalculate_reliability_study(elements, result: ReliabilityResult) -> ReliabilityResult:
    config: ReliabilityStudyConfig = result.config
    data = DATA_MANAGER.get_data_from_data_label(
        data_label=config.data_source,
        current_result_id=result.unique_id,
    )

    df = data.get_dataframe(columns=config.column_selector[0], map_ordinal=True)

    scale_columns = config.column_selector[1]
    scale_column = scale_columns[0] if scale_columns else None
    correlation_type = CORRELATION_TYPE_MAP[config.correlation_type]

    correlation_type_map = {
        CorrelationType.PEARSON: "pearson",
        CorrelationType.SPEARMAN: "spearman",
        CorrelationType.KENDALL: "kendall",
    }

    if correlation_type in correlation_type_map.keys():
        correlation_matrix = df.corr(method=correlation_type_map[correlation_type])
        alpha = cronbach_alpha(correlation_matrix.values)
    else:
        # Check if all columns have most 2 unique values
        if not all(df[col].nunique() <= 2 for col in df.columns):
            msg = t("reliability.msg.binary_required")
            result.set_placeholder(msg)
            logging.debug(msg)
            return result
        # Scale all columns to 0..1
        for col in df.columns:
            df[col] = df[col] - df[col].min()
            if df[col].max() != 0:
                df[col] = df[col] / df[col].max()

        if correlation_type == CorrelationType.PHI:
            correlation_matrix = phi_correlation_table(df)
        else:
            correlation_matrix = tetrachoric_corr_matrix(df)[0]

        alpha = cronbach_alpha(correlation_matrix.values)

    table = HTMLTableV2(table_caption=t("reliability.caption.cronbach"))
    table.add_title_row_apa(
        Row(
            [
                Cell(),
                Cell(t("reliability.caption.cronbach"), center=True),
            ]
        )
    )

    table.add_single_row_apa(
        Row(
            [
                Cell(scale_column if scale_column is not None else "", push_to_left=True),
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
