#
#  Copyright (c) 2023 -- 2024 StatPrism Team. All rights reserved.
#

from src.common.constant import MDASH
from src.common.decorators import log_function
from src.common.result.classes.html_result import Cell, HTMLTableV2, Row
from src.common.result.classes.plot_result import Line, PlotV2
from src.data_panel.data import Data
from src.modules.v2.result import V2Result


@log_function
def recalculate_v2_study(data: Data, result: V2Result) -> V2Result:
    result.update_header()
    df = data.get_dataframe(filters=result.config.filters, columns=result.config.selected_columns)

    table = HTMLTableV2(table_caption="Column Parameters")
    table.add_title_row_apa(
        Row(
            [
                Cell("Column"),
                Cell("Type"),
                Cell("Dtype"),
                Cell("Numeric"),
                Cell("Order"),
                Cell("First Value"),
                Cell("Max Value"),
                Cell("Min Value"),
                Cell("Mean Value"),
            ]
        )
    )

    for col in result.config.selected_columns:
        table.add_single_row_apa(
            Row(
                [
                    Cell(col),
                    Cell(data[col].column_type),
                    Cell(data[col].column_dtype),
                    Cell(data[col].is_numeric),
                    Cell(data[col].order),
                    Cell(df[col].iloc[0]),
                    Cell(df[col].max()),
                    Cell(df[col].min()),
                    Cell(df[col].mean()) if data[col].is_numeric else Cell(MDASH),
                ]
            )
        )

    plot = PlotV2(
        items=[Line(x=df.iloc[:, 0], y=df.iloc[:, 1], label="Line 1")],
        title="Plot",
        x_axis_title="X",
        y_axis_title="y",
    )

    result.result_elements = [table, plot]  # , table.split_table(max_cols=4)]
    return result
