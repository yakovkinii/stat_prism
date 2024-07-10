from src.common.constant import MDASH
from src.common.utility import smart_comma_join
from src.results_panel.results.common.html_element import HTMLTable, Row, Cell


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
        return "&lt; .001"
    else:
        return f"{round(p, decimals):.{decimals}f}".replace("0.", ".")


def get_table(columns, correlation_matrix, p_matrix, df_matrix, compact, table_name):
    n_subrows = 1 if compact else 3
    html = f'<div class="table-name-apa">Table {table_name}.</div> <br>'
    html += (
        f'<div class="table-title-apa">Correlations between '
        + smart_comma_join([f"'{var}'" for var in columns])
        + ".</div><br>"
    )
    html += "<table>"
    html += "<tr>"
    html += '<td  class="thick-border-bottom thick-border-top thin-border-left"></td>'
    if not compact:
        html += '<td  class="thin-border-left thin-border-right thick-border-bottom thick-border-top"></td>'
    for column in columns:
        html += (
            f'<td colspan="2" class="thin-border-left thick-border-bottom thick-border-top multiline'
            f' thin-border-right"><span>{column}</span></td>'
        )
    html += "</tr>"

    for i_row, row in enumerate(columns):
        for sub_row in range(n_subrows):
            last = i_row == len(columns) - 1
            html += "<tr>"
            if sub_row == 0:  # r
                html += (
                    f'<td rowspan="{n_subrows}" class="thin-border-top '
                    + ("thick-border-bottom" if last else f"thin-border-bottom")
                    + " multiline"
                    + f' thin-border-left"><span>{row}</span></td>'
                )
                if not compact:
                    html += f'<td class="thin-border-left thin-border-top nowrap"><span>Pearson\'s r</span></td>'
                for i_column, column in enumerate(columns):
                    if i_column < i_row:
                        html += (
                            '<span class="thin-border-left align-right thin-border-top nowrap'
                            + (" thin-border-bottom" if compact and not last else "")
                            + (" thick-border-bottom" if compact and last else "")
                            + '"><td class="align-right">'
                            + format_r_apa(
                                correlation_matrix.loc[row, column],
                            )
                            + "</td></span>"
                        )
                        html += (
                            '<td class="align-left thin-border-top thin-border-right'
                            + (" thin-border-bottom" if compact and not last else "")
                            + (" thick-border-bottom" if compact and last else "")
                            + '"><span class="align-left">'
                            + get_stars(p_matrix.loc[row, column])
                            + "</span></td>"
                        )
                    elif i_column == i_row:
                        html += (
                            f'<td class="thin-border-left align-right thin-border-top'
                            + (" thin-border-bottom" if compact and not last else "")
                            + (" thick-border-bottom" if compact and last else "")
                            + '"><span>&mdash;</span></td>'
                        )
                        html += (
                            f'<td class="thin-border-top thin-border-right'
                            + (" thin-border-bottom" if compact and not last else "")
                            + (" thick-border-bottom" if compact and last else "")
                            + '"><span></span></td>'
                        )
                    else:
                        html += (
                            f'<td class="thin-border-left align-right thin-border-top'
                            + (" thin-border-bottom" if compact and not last else "")
                            + (" thick-border-bottom" if compact and last else "")
                            + '"><span></span></td>'
                        )
                        html += (
                            f'<td class="thin-border-top thin-border-right'
                            + (" thin-border-bottom" if compact and not last else "")
                            + (" thick-border-bottom" if compact and last else "")
                            + '"><span></span></td>'
                        )

            if sub_row == 1:  # p
                html += '<td class="thin-border-left"><span>p-value</span></td>'
                for i_column, column in enumerate(columns):
                    if i_column < i_row:
                        html += (
                            f'<span class="thin-border-left align-right nowrap"><td class="align-right">'
                            + format_p_apa(p_matrix.loc[row, column])
                            + "</td></span>"
                        )
                    elif i_column == i_row:
                        html += '<td class="thin-border-left align-right"><span>&mdash;</span></td>'
                    else:
                        html += '<td class="thin-border-left align-right"><span></span></td>'
                    html += '<td class="thin-border-right"><span></span></td>'

            if sub_row == 2:  # df
                html += (
                    '<td class="thin-border-left '
                    + ("thick-border-bottom" if last else "thin-border-bottom")
                    + '"><span>df</span></td>'
                )
                for i_column, column in enumerate(columns):
                    if i_column < i_row:
                        html += (
                            f'<td class="thin-border-left align-right '
                            + ("thick-border-bottom" if last else "thin-border-bottom")
                            + '">'
                            + str(df_matrix.loc[row, column])
                            + "</td>"
                        )
                    elif i_column == i_row:
                        html += (
                            f'<td class="thin-border-left align-right '
                            + ("thick-border-bottom" if last else "thin-border-bottom")
                            + '"><span>'
                            + f"&mdash;</span></td>"
                        )
                    else:
                        html += (
                            f'<td class="thin-border-left align-right '
                            + ("thick-border-bottom" if last else "thin-border-bottom")
                            + f'"><span></span></td>'
                        )
                    html += (
                        '<td class="thin-border-right '
                        + ("thick-border-bottom" if last else "thin-border-bottom")
                        + '"><span></span></td>'
                    )

            html += "</tr>"

    html += "</table>"
    html += '<div class="footnote"> <i>Note.</i> * p &lt; .05; ** p &lt; .01; *** p &lt; .001</div>'
    # print(html)
    return html


def get_table_compact(columns, correlation_matrix, p_matrix) -> HTMLTable:
    table = HTMLTable([])

    table.table_id = "1"
    table.table_caption = "Correlations between " + smart_comma_join([f"'{var}'" for var in columns]) + "."

    # Add header
    table.add_single_row_apa(Row([Cell()] + [Cell(column, col_span=2, center=True) for column in columns]))

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

    table.table_note = "* p &lt; .05; ** p &lt; .01; *** p &lt; .001"

    return table


def get_table_full(columns, correlation_matrix, p_matrix, df_matrix) -> HTMLTable:
    table = HTMLTable([])

    table.table_id = "1"
    table.table_caption = "Correlations between " + smart_comma_join([f"'{var}'" for var in columns]) + "."

    # Add header
    table.add_single_row_apa(Row([Cell(col_span=2)] + [Cell(column, col_span=2, center=True) for column in columns]))

    # Add matrix
    for i_row, row in enumerate(columns):
        table_row_1 = [Cell(row, row_span=3), Cell("Pearson's r", no_wrap=True)]
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

        table_row_2 = [Cell("p-value", no_wrap=True)]
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

    table.table_note = "* p &lt; .05; ** p &lt; .01; *** p &lt; .001"

    return table
