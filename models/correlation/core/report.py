from core.utility import smart_comma_join


def format_r_apa(r, decimals=2):
    return f'{round(r, decimals):.{decimals}f}'.replace('0.','.')


def get_strength(r):
    if abs(round(r,2))>0.5:
        return 'strong'
    elif abs(round(r,2))>0.3:
        return 'moderate'
    elif abs(round(r,2))>0.1:
        return 'weak'
    else:
        return 'very weak'


def get_sign(r):
    if r>0:
        return 'positive'
    else:
        return 'negative'


def format_p_apa(p, decimals=3):
    if p < 0.001:
        return "p &lt; .001"
    else:
        return f"p = {round(p, decimals):.{decimals}f}".replace('0.', '.')


def format_apa(r,p,df):
    return f'r({df}) = {format_r_apa(r)}, {format_p_apa(p)}'


def get_statement_2_items(r,p,df):
    if p>0.05:
        return f"The results indicated that the relationship between the two variables " \
               f"was not significant, {format_apa(r,p,df)}. "
    else:
        text=f'There was a {get_strength(r)} {get_sign(r)} correlation between the two variables, {format_apa(r,p,df)}. '

        if abs(r)<0.1:
            text+='Although statistically significant, the relationship is negligible. '
    return text

def get_statement_multiple_items(r,p,df, var1, var2):
    if p>0.05:
        return f"The results indicated that the relationship between the variables '{var1}' and '{var2}' " \
               f"was not significant, {format_apa(r,p,df)}. "
    else:
        text=f"There was a {get_strength(r)} {get_sign(r)} correlation between the the variables '{var1}' and '{var2}', {format_apa(r,p,df)}. "

        if abs(r)<0.1:
            text+='Although statistically significant, the relationship is negligible. '
    return text




def get_report(columns, correlation_matrix, p_matrix, df_matrix):
    text = (f"A Pearson correlation coefficient was computed to assess the linear relationship between the variables "+
    smart_comma_join([f"'{var}'" for var in columns])
            +
            '. '
            )

    if len(columns) == 2:
        return text+get_statement_2_items(r=correlation_matrix.loc[columns[1],columns[0]], p=p_matrix.loc[columns[1],columns[0]],
                                          df=df_matrix.loc[columns[1],columns[0]])

    for i_row, row in enumerate(columns):
        for i_column, column in enumerate(columns):
            if i_column < i_row:
                text += get_statement_multiple_items(r=correlation_matrix.loc[row,column], p=p_matrix.loc[row,column],
                                                     df=df_matrix.loc[row,column], var1=row, var2=column)
    return text
