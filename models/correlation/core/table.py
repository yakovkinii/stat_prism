from core.utility import smart_comma_join


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
    html = f'<div class="table-name-apa">Table {table_name}.</div>'
    html += (
        f'<div class="table-title-apa">Correlations between '
        + smart_comma_join([f"'{var}'" for var in columns])
        + ".</div>"
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
    print(html)
    return html
