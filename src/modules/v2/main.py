#
#  Copyright (c) 2023 -- 2024 StatPrism Team. All rights reserved.
#

import logging
from typing import Dict, Union

import pandas as pd

from src.common.decorators import log_function
from src.common.result.classes.html_result import Cell, HTMLTableV2, Row
from src.modules.v2.result import V2Result, V2StudyConfig


@log_function
def recalculate_v2_study(
    df: pd.DataFrame, result: V2Result, ordinal_orders: Dict[str, Dict[Union[int, float, str], int]]
) -> V2Result:
    config: V2StudyConfig = result.config
    result.update_header()

    if len(config.filters) > 0:
        for filter_settings in config.filters:
            query = filter_settings.get_query()
            logging.debug(f"Applying Filter: {query}")
            df = df.query(query)
    else:
        logging.debug("No filter applied")

    df = df[config.selected_columns]

    table = HTMLTableV2(table_caption="Stats Value")
    table.add_title_row_apa(
        Row([Cell("Column"), Cell("First Value"), Cell("Max Value"), Cell("Min Value"), Cell("Mean Value")])
    )
    for col in config.selected_columns:
        table.add_single_row_apa(
            Row([Cell(col), Cell(df[col].iloc[0]), Cell(df[col].max()), Cell(df[col].min()), Cell(df[col].mean())])
        )

    result.result_elements = [table] + table.split_table(max_cols=2)
    return result
