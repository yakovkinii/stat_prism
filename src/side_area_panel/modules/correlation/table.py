#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from src.common.constant import MDASH
from src.common.translations import t
from src.side_area_panel.modules.common.column_numbering import ColumnNumbering
from src.side_area_panel.modules.common.result.html_result import Cell, HTMLTableV2, Row
from src.side_area_panel.modules.common.utility import (
    format_p_apa_exact,
    format_r_apa,
    get_stars,
    smart_comma_join,
)
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


def _numbering(numbering):
    """Use the given numbering, or a disabled pass-through one when None."""
    return numbering if numbering is not None else ColumnNumbering([], False)


def _caption(kind, columns):
    name = t(_TABLE_NAME_KEY[kind])
    variables = smart_comma_join([f"«{var}»" for var in columns])
    return t("correlation.table.caption", name=name, vars=variables)


def _cross_caption(kind, rows, cols):
    name = t(_TABLE_NAME_KEY[kind])
    row_vars = smart_comma_join([f"«{var}»" for var in rows])
    col_vars = smart_comma_join([f"«{var}»" for var in cols])
    return t("correlation.table.cross_caption", name=name, rows=row_vars, cols=col_vars)


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


def get_table_compact(columns, correlation_matrix, p_matrix, kind: CorrelationType, numbering=None) -> HTMLTableV2:
    numbering = _numbering(numbering)
    table = HTMLTableV2(table_caption=_caption(kind, columns))

    # Add header
    table.add_title_row_apa(
        Row([Cell()] + [Cell(numbering.label(column), col_span=2, center=True) for column in columns])
    )

    # Add matrix
    for i_row, row in enumerate(columns):
        table_row = [Cell(numbering.label(row))]
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

    table.table_note = numbering.append_to_note(t("correlation.table.significance_note"))

    return table


def _ci_cell(ci_value):
    """A doubled CI cell pair ('[lo, hi]' across both sub-columns), or blank when no CI."""
    text = ci_value if isinstance(ci_value, str) else ""
    return [
        Cell(text, push_to_right=True, is_doubled=True, no_wrap=True),
        Cell(push_to_left=True, is_doubled=True),
    ]


def get_table_cross(
    rows, cols, correlation_matrix, p_matrix, df_matrix, kind: CorrelationType, compact: bool, ci_matrix=None, numbering=None
) -> HTMLTableV2:
    """Rectangular two-set correlation table: `rows` down the side, `cols` across the top,
    every cell filled (full grid). Compact shows r + stars; full stacks r / p / df (/ CI)."""
    numbering = _numbering(numbering)
    table = HTMLTableV2(table_caption=_cross_caption(kind, rows, cols))
    hide_df_matrix = all(df_matrix.isnull().values.flatten())
    show_ci = ci_matrix is not None

    if compact:
        table.add_title_row_apa(Row([Cell()] + [Cell(numbering.label(col), col_span=2, center=True) for col in cols]))
        for row in rows:
            table_row = [Cell(numbering.label(row))]
            for col in cols:
                table_row.append(
                    Cell(format_r_apa(correlation_matrix.loc[row, col]), push_to_right=True, is_doubled=True, no_wrap=True)
                )
                table_row.append(Cell(get_stars(p_matrix.loc[row, col]), push_to_left=True, is_doubled=True))
            table.add_single_row_apa(Row(table_row))
        table.table_note = numbering.append_to_note(t("correlation.table.significance_note"))
        return table

    # Full: r / p (/ df) (/ CI) stacked per row.
    n_stack = 2 + (0 if hide_df_matrix else 1) + (1 if show_ci else 0)
    table.add_title_row_apa(Row([Cell(col_span=2)] + [Cell(numbering.label(col), col_span=2, center=True) for col in cols]))
    for row in rows:
        table_row_1 = [
            Cell(numbering.label(row), row_span=n_stack),
            Cell(get_correlation_short_name(kind), no_wrap=True),
        ]
        for col in cols:
            table_row_1.append(
                Cell(format_r_apa(correlation_matrix.loc[row, col]), push_to_right=True, is_doubled=True, no_wrap=True)
            )
            table_row_1.append(Cell(get_stars(p_matrix.loc[row, col]), push_to_left=True, is_doubled=True))

        table_row_2 = [Cell(t("common.p_value"), no_wrap=True)]
        for col in cols:
            table_row_2.append(
                Cell(format_p_apa_exact(p_matrix.loc[row, col]), push_to_right=True, is_doubled=True, no_wrap=True)
            )
            table_row_2.append(Cell(push_to_left=True, is_doubled=True))

        stacked = [Row(table_row_1), Row(table_row_2)]

        if not hide_df_matrix:
            table_row_3 = [Cell("df", no_wrap=True)]
            for col in cols:
                table_row_3.append(
                    Cell(str(df_matrix.loc[row, col]), push_to_right=True, is_doubled=True, no_wrap=True)
                )
                table_row_3.append(Cell(push_to_left=True, is_doubled=True))
            stacked.append(Row(table_row_3))

        if show_ci:
            table_row_ci = [Cell(t("common.ci_95"), no_wrap=True)]
            for col in cols:
                table_row_ci += _ci_cell(ci_matrix.loc[row, col])
            stacked.append(Row(table_row_ci))

        table.add_multirow_apa(stacked)

    table.table_note = numbering.append_to_note(t("correlation.table.significance_note"))
    return table


def get_table_full(columns, correlation_matrix, p_matrix, df_matrix, kind: CorrelationType, ci_matrix=None, numbering=None) -> HTMLTableV2:
    numbering = _numbering(numbering)
    table = HTMLTableV2(table_caption=_caption(kind, columns))

    hide_df_matrix = all(df_matrix.isnull().values.flatten())
    show_ci = ci_matrix is not None
    n_stack = 2 + (0 if hide_df_matrix else 1) + (1 if show_ci else 0)

    # Add header
    table.add_title_row_apa(Row([Cell(col_span=2)] + [Cell(numbering.label(column), col_span=2, center=True) for column in columns]))

    # Add matrix
    for i_row, row in enumerate(columns):
        table_row_1 = [
            Cell(numbering.label(row), row_span=n_stack),
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
                    Cell(format_p_apa_exact(p_matrix.loc[row, column]), push_to_right=True, is_doubled=True, no_wrap=True)
                )
                table_row_2.append(Cell(push_to_left=True, is_doubled=True))
            elif i_column == i_row:
                table_row_2.append(Cell(MDASH, push_to_right=True, is_doubled=True))
                table_row_2.append(Cell(push_to_left=True, is_doubled=True))
            else:
                table_row_2.append(Cell(push_to_right=True, is_doubled=True))
                table_row_2.append(Cell(push_to_left=True, is_doubled=True))

        stacked = [Row(table_row_1), Row(table_row_2)]

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
            stacked.append(Row(table_row_3))

        if show_ci:
            table_row_ci = [Cell(t("common.ci_95"), no_wrap=True)]
            for i_column, column in enumerate(columns):
                if i_column < i_row:
                    table_row_ci += _ci_cell(ci_matrix.loc[row, column])
                elif i_column == i_row:
                    table_row_ci.append(Cell(MDASH, push_to_right=True, is_doubled=True))
                    table_row_ci.append(Cell(push_to_left=True, is_doubled=True))
                else:
                    table_row_ci.append(Cell(push_to_right=True, is_doubled=True))
                    table_row_ci.append(Cell(push_to_left=True, is_doubled=True))
            stacked.append(Row(table_row_ci))

        table.add_multirow_apa(stacked)

    table.table_note = numbering.append_to_note(t("correlation.table.significance_note"))

    return table
