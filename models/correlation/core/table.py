def format_r_apa(r, decimals=2):
    return f'{round(r, decimals):.{decimals}f}'.replace('0.','.')


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
        return f"{round(p, decimals):.{decimals}f}".replace('0.', '.')


def get_table(columns, correlation_matrix, p_matrix, df_matrix, compact):

    n_subrows = 1 if compact else 3
    html = "<table>"
    html += "<tr>"
    html += '<td  class="thick-border-bottom thin-border-top thin-border-left"></td>'
    if not compact:
        html += '<td  class="thin-border-left thin-border-right thick-border-bottom thin-border-top"></td>'
    for column in columns:
        html += f'<td colspan="2" class="thin-border-left thick-border-bottom thin-border-top multiline' \
                f' thin-border-right"><span>{column}</span></td>'
    html += "</tr>"

    for i_row, row in enumerate(columns):
        for sub_row in range(n_subrows):
            html += "<tr>"
            if sub_row == 0:  # r
                html += (
                    f'<td rowspan="{n_subrows}" class="thin-border-top thin-border-bottom multiline'
                    f' thin-border-left"><span>{row}</span></td>'
                )
                if not compact:
                    html += f'<td class="thin-border-left thin-border-top nowrap"><span>Pearson\'s r</span></td>'
                for i_column, column in enumerate(columns):
                    if i_column < i_row:
                        html += (
                            '<td class="thin-border-left align-right thin-border-top nowrap' +
                            (' thin-border-bottom' if compact else '')+
                            '"><span>'
                            + format_r_apa(
                                correlation_matrix.loc[row, column],
                            )
                            + "</span></td>"
                        )
                        html += (
                            '<td class="align-left thin-border-top thin-border-right' +
                            (' thin-border-bottom' if compact else '')+
                            '"><span class="align-left">'
                            + get_stars(p_matrix.loc[row, column])
                            + "</span></td>"
                        )
                    elif i_column == i_row:
                        html += (f'<td class="thin-border-left align-right thin-border-top' +
                            (' thin-border-bottom' if compact else '')+
                            '"><span>&mdash;</span></td>')
                        html += (f'<td class="thin-border-top thin-border-right' +
                            (' thin-border-bottom' if compact else '')+
                            '"><span></span></td>')
                    else:
                        html += (f'<td class="thin-border-left align-right thin-border-top' +
                            (' thin-border-bottom' if compact else '')+
                            '"><span></span></td>')
                        html +=( f'<td class="thin-border-top thin-border-right' +
                            (' thin-border-bottom' if compact else '')+
                            '"><span></span></td>')

            if sub_row == 1:  # p
                html += '<td class="thin-border-left"><span>p-value</span></td>'
                for i_column, column in enumerate(columns):
                    if i_column < i_row:
                        html += (
                            f'<td class="thin-border-left align-right nowrap"><span>'
                            + format_p_apa(p_matrix.loc[row, column])
                            + "</span></td>"
                        )
                    elif i_column == i_row:
                        html += f'<td class="thin-border-left align-right"><span>&mdash;</span></td>'
                    else:
                        html += f'<td class="thin-border-left align-right"><span></span></td>'
                    html += '<td class="thin-border-right"><span></span></td>'

            if sub_row == 2:  # df
                html += f'<td class="thin-border-left thin-border-bottom"><span>df</span></td>'
                for i_column, column in enumerate(columns):
                    if i_column < i_row:
                        html += (f'<td class="thin-border-left align-right thin-border-bottom"><span>'
                        +str(df_matrix.loc[row, column])
                        +'</span></td>')
                    elif i_column == i_row:
                        html += f'<td class="thin-border-left align-right thin-border-bottom"><span>' \
                                f'&mdash;</span></td>'
                    else:
                        html += f'<td class="thin-border-left align-right thin-border-bottom"><span></span></td>'
                    html += '<td class="thin-border-right thin-border-bottom"><span></span></td>'

            html += "</tr>"

    html += "</table>"
    html += '<div class="footnote">* p &lt; .05; ** p &lt; .01; *** p &lt; .001</div>'
    print(html)
    return html
