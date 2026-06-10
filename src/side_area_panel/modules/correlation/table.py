#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from src.common.constant import MDASH
from src.common.translations import t
from src.side_area_panel.modules.common.result.html_result import Cell, HTMLTableV2, Row
from src.side_area_panel.modules.common.utility import smart_comma_join
from src.side_area_panel.modules.correlation.correlation_result import CorrelationType

_TABLE_NAME_KEY = {
    CorrelationType.PEARSON: "correlation.table.name.pearson",
    CorrelationType.SPEARMAN: "correlation.table.name.spearman",
    CorrelationType.KENDALL: "correlation.table.name.kendall",
    CorrelationType.PHI: "correlation.table.name.phi",
    CorrelationType.TETRACHORIC: "correlation.table.name.tetrachoric",
    CorrelationType.POLYCHORIC: "correlation.table.name.polychoric",
}
if hasattr(CorrelationType, "KENDALL_C"):
    _TABLE_NAME_KEY[CorrelationType.KENDALL_C] = "correlation.table.name.kendall_c"


def _caption(kind, columns):
    name = t(_TABLE_NAME_KEY[kind])
    variables = smart_comma_join([f"«{var}»" for var in columns])
    return t("correlation.table.caption", name=name, vars=variables)


def format_r_apa(r, decimals=2):
    return str(f"{round(r, decimals):.{decimals}f}".replace("0.", "."))


def get_stars(p):
    if p < 0.001:
        return "***"
    elif p < 0.01:
        return "**"
    elif p < 0.05:
        return "*"
    else:
        return ""


def format_p_apa(p, decimals=3):
    if p < 0.001:
        return "&lt;&nbsp;.001"
    else:
        return f"{round(p, decimals):.{decimals}f}".replace("0.", ".")


def get_correlation_short_name(kind: CorrelationType) -> str:
    if kind == CorrelationType.PEARSON:
        return "r"
    elif kind == CorrelationType.SPEARMAN:
        return "rs"
    elif kind == CorrelationType.KENDALL:
        return "τ"
    elif kind == CorrelationType.KENDALL_C:
        return "τ<sub>c</sub>"
    elif kind == CorrelationType.PHI:
        return "φ"
    elif kind == CorrelationType.TETRACHORIC:
        return "ρt"
    elif kind == CorrelationType.POLYCHORIC:
        return "ρpc"
    else:
        raise ValueError(f"Invalid correlation type: {kind}")


def get_table_compact(columns, correlation_matrix, p_matrix, kind: CorrelationType) -> HTMLTableV2:
    table = HTMLTableV2(table_caption=_caption(kind, columns))

    # Add header
    table.add_title_row_apa(Row([Cell()] + [Cell(column, col_span=2, center=True) for column in columns]))

    # Add matrix
    for i_row, row in enumerate(columns):
        table_row = [Cell(row)]
        for i_column, column in enumerate(columns):
            if i_column < i_row:
                table_row.append(
                    Cell(
                        format_r_apa(correlation_matrix.loc[row, column]),
                        push_to_right=True,
                        is_doubled=True,
                        no_wrap=True,
                    )
                )
                table_row.append(Cell(get_stars(p_matrix.loc[row, column]), push_to_left=True, is_doubled=True))
            elif i_column == i_row:
                table_row.append(Cell(MDASH, push_to_right=True, is_doubled=True))
                table_row.append(Cell(push_to_left=True, is_doubled=True))
            else:
                table_row.append(Cell(push_to_right=True, is_doubled=True))
                table_row.append(Cell(push_to_left=True, is_doubled=True))
        table.add_single_row_apa(Row(table_row))

    table.table_note = t("correlation.table.significance_note")

    return table


def get_table_full(columns, correlation_matrix, p_matrix, df_matrix, kind: CorrelationType) -> HTMLTableV2:
    table = HTMLTableV2(table_caption=_caption(kind, columns))

    hide_df_matrix = all(df_matrix.isnull().values.flatten())

    # Add header
    table.add_title_row_apa(Row([Cell(col_span=2)] + [Cell(column, col_span=2, center=True) for column in columns]))

    # Add matrix
    for i_row, row in enumerate(columns):
        table_row_1 = [
            Cell(row, row_span=3 if not hide_df_matrix else 2),
            Cell(get_correlation_short_name(kind), no_wrap=True),
        ]
        for i_column, column in enumerate(columns):
            if i_column < i_row:
                table_row_1.append(
                    Cell(
                        format_r_apa(correlation_matrix.loc[row, column]),
                        push_to_right=True,
                        is_doubled=True,
                        no_wrap=True,
                    )
                )
                table_row_1.append(Cell(get_stars(p_matrix.loc[row, column]), push_to_left=True, is_doubled=True))
            elif i_column == i_row:
                table_row_1.append(Cell(MDASH, push_to_right=True, is_doubled=True))
                table_row_1.append(Cell(push_to_left=True, is_doubled=True))
            else:
                table_row_1.append(Cell(push_to_right=True, is_doubled=True))
                table_row_1.append(Cell(push_to_left=True, is_doubled=True))

        table_row_2 = [Cell(t("common.p_value"), no_wrap=True)]
        for i_column, column in enumerate(columns):
            if i_column < i_row:
                table_row_2.append(
                    Cell(format_p_apa(p_matrix.loc[row, column]), push_to_right=True, is_doubled=True, no_wrap=True)
                )
                table_row_2.append(Cell(push_to_left=True, is_doubled=True))
            elif i_column == i_row:
                table_row_2.append(Cell(MDASH, push_to_right=True, is_doubled=True))
                table_row_2.append(Cell(push_to_left=True, is_doubled=True))
            else:
                table_row_2.append(Cell(push_to_right=True, is_doubled=True))
                table_row_2.append(Cell(push_to_left=True, is_doubled=True))

        if not hide_df_matrix:
            table_row_3 = [Cell("df", no_wrap=True)]
            for i_column, column in enumerate(columns):
                if i_column < i_row:
                    table_row_3.append(
                        Cell(str(df_matrix.loc[row, column]), push_to_right=True, is_doubled=True, no_wrap=True)
                    )
                    table_row_3.append(Cell(push_to_left=True, is_doubled=True))
                elif i_column == i_row:
                    table_row_3.append(Cell(MDASH, push_to_right=True, is_doubled=True))
                    table_row_3.append(Cell(push_to_left=True, is_doubled=True))
                else:
                    table_row_3.append(Cell(push_to_right=True, is_doubled=True))
                    table_row_3.append(Cell(push_to_left=True, is_doubled=True))
            table.add_multirow_apa(
                [
                    Row(table_row_1),
                    Row(table_row_2),
                    Row(table_row_3),
                ]
            )
        else:
            table.add_multirow_apa(
                [
                    Row(table_row_1),
                    Row(table_row_2),
                ]
            )

    table.table_note = t("correlation.table.significance_note")

    return table
