from src.common.result.classes.html_result import Cell, HTMLTable, Row
from src.common.utility import smart_comma_join
from src.modules.cross_correlation.result import CrossCorrelationType


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


def get_table_compact(rows, columns, correlation_matrix, p_matrix, kind: CrossCorrelationType) -> HTMLTable:
    table = HTMLTable([])

    if kind == CrossCorrelationType.PEARSON:
        correlation_name = "Pearson cross-correlations"
    elif kind == CrossCorrelationType.SPEARMAN:
        correlation_name = "Spearman rank cross-correlations"
    elif kind == CrossCorrelationType.KENDALL:
        correlation_name = "Kendall rank cross-correlations"
    else:
        raise ValueError(f"Unknown cross-correlation type: {kind}")

    table.table_caption = (
        f"{correlation_name} between "
        + smart_comma_join([f"'{var}'" for var in rows])
        + " and "
        + smart_comma_join([f"'{var}'" for var in columns])
        + "."
    )

    # Add header
    table.add_title_row_apa(Row([Cell()] + [Cell(column, col_span=2, center=True) for column in columns]))

    # Add matrix
    for i_row, row in enumerate(rows):
        table_row = [Cell(row)]
        for i_column, column in enumerate(columns):
            table_row.append(
                Cell(
                    format_r_apa(correlation_matrix.loc[row, column]),
                    push_to_right=True,
                    is_doubled=True,
                    no_wrap=True,
                )
            )
            table_row.append(Cell(get_stars(p_matrix.loc[row, column]), push_to_left=True, is_doubled=True))
        table.add_single_row_apa(Row(table_row))

    table.table_note = "* p &lt; .05; ** p &lt; .01; *** p &lt; .001"

    return table


def get_table_full(rows, columns, correlation_matrix, p_matrix, df_matrix, kind: CrossCorrelationType) -> HTMLTable:
    if kind == CrossCorrelationType.PEARSON:
        correlation_short_name = "Pearson's&nbsp;r"
        correlation_name = "Pearson cross-correlations"
    elif kind == CrossCorrelationType.SPEARMAN:
        correlation_short_name = "Spearman's&nbsp;r"
        correlation_name = "Spearman rank cross-correlations"
    elif kind == CrossCorrelationType.KENDALL:
        correlation_short_name = "Kendall's&nbsp;τ"
        correlation_name = "Kendall rank cross-correlations"
    else:
        raise ValueError(f"Invalid correlation type: {kind}")

    table = HTMLTable([])

    table.table_caption = (
        f"{correlation_name} between "
        + smart_comma_join([f"'{var}'" for var in rows])
        + " and "
        + smart_comma_join([f"'{var}'" for var in columns])
        + "."
    )

    # Add header
    table.add_title_row_apa(Row([Cell(col_span=2)] + [Cell(column, col_span=2, center=True) for column in columns]))

    # Add matrix
    for i_row, row in enumerate(rows):
        table_row_1 = [Cell(row, row_span=3), Cell(correlation_short_name, no_wrap=True)]
        for i_column, column in enumerate(columns):
            table_row_1.append(
                Cell(
                    format_r_apa(correlation_matrix.loc[row, column]),
                    push_to_right=True,
                    is_doubled=True,
                    no_wrap=True,
                )
            )
            table_row_1.append(Cell(get_stars(p_matrix.loc[row, column]), push_to_left=True, is_doubled=True))

        table_row_2 = [Cell("p-value", no_wrap=True)]
        for i_column, column in enumerate(columns):
            table_row_2.append(
                Cell(format_p_apa(p_matrix.loc[row, column]), push_to_right=True, is_doubled=True, no_wrap=True)
            )
            table_row_2.append(Cell(push_to_left=True, is_doubled=True))

        table_row_3 = [Cell("df", no_wrap=True)]
        for i_column, column in enumerate(columns):
            table_row_3.append(Cell(str(df_matrix.loc[row, column]), push_to_right=True, is_doubled=True, no_wrap=True))
            table_row_3.append(Cell(push_to_left=True, is_doubled=True))

        table.add_multirow_apa(
            [
                Row(table_row_1),
                Row(table_row_2),
                Row(table_row_3),
            ]
        )

    table.table_note = "* p &lt; .05; ** p &lt; .01; *** p &lt; .001"

    return table
