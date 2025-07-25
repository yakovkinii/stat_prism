#  Copyright (c) 2023 StatPrism Team. All rights reserved.



import numpy as np

from src.common.constant import TABLE_OR_PLOT_ID_PLACEHOLDER
from src.modules.common.utility import smart_comma_join
from src.modules.correlation.result import CorrelationType


def format_r_apa(r, decimals=2):
    return f"{round(r, decimals):.{decimals}f}".replace("0.", ".")


def get_strength(r):
    if abs(round(r, 2)) > 0.5:
        return "strong"
    elif abs(round(r, 2)) > 0.3:
        return "moderate"
    elif abs(round(r, 2)) > 0.1:
        return "weak"
    else:
        return "very weak"


def get_sign(r):
    if r > 0:
        return "positive"
    else:
        return "negative"


def format_p_apa(p, decimals=3):
    if p < 0.001:
        return "p &lt; .001"
    else:
        return f"p = {round(p, decimals):.{decimals}f}".replace("0.", ".")


def format_apa(r, p, df, letter):
    if np.isnan(df):
        return f"{letter} = {format_r_apa(r)}, {format_p_apa(p)}"
    return f"{letter}({df}) = {format_r_apa(r)}, {format_p_apa(p)}"


def get_statement_2_items(r, p, df, letter):
    if p > 0.05:
        return (
            f"The results indicated that the relationship between the two variables "
            f"was not significant, {format_apa(r, p, df,letter)}. "
        )
    else:
        text = (
            f"There was a {get_strength(r)} {get_sign(r)} correlation between "
            f"the two variables, {format_apa(r, p, df,letter)}. "
        )

        if abs(r) < 0.1:
            text += "Although statistically significant, the relationship is negligible. "
    return text


def get_statement_multiple_items(r, p, df, var1, var2, id1, id2, id3, letter):
    if p > 0.05:
        return [
            f"The correlation between '{var1}' and '{var2}' was found to be non-significant,"
            f" {format_apa(r, p, df,letter)}. ",
            f"The results indicated that the relationship between the variables '{var1}' and '{var2}' "
            f"was not significant, {format_apa(r, p, df,letter)}. ",
            f"There was no significant correlation identified between '{var1}' and '{var2}', "
            f"{format_apa(r, p, df,letter)}. ",
        ][id1.get() % 3]
    else:
        text = [
            f"There was a {get_strength(r)} {get_sign(r)} correlation between the the "
            f"variables '{var1}' and '{var2}', {format_apa(r, p, df,letter)}. ",
            f"A {get_strength(r)} and {get_sign(r)} correlation was observed between '{var1}' and '{var2}',"
            f" {format_apa(r, p, df,letter)}. ",
            f"The variables '{var1}' and '{var2}' showed a {get_strength(r)} and {get_sign(r)} correlation, "
            f"{format_apa(r, p, df,letter)}. ",
        ][id2.get() % 3]

        if abs(r) < 0.1:
            text += [
                "Although statistically significant, the relationship is negligible. ",
                "While the relationship is statistically significant, its impact is minimal. ",
                "Though significant in statistical terms, the relationship is inconsequential in practicality. ",
            ][id3.get() % 3]
    return text


class ID:
    def __init__(self):
        self.i = -1

    def get(self):
        self.i = self.i + 1
        return self.i


def get_report(columns, correlation_matrix, p_matrix, df_matrix, report_non_significant, kind: CorrelationType):
    id1 = ID()
    id2 = ID()
    id3 = ID()
    if kind == CorrelationType.PEARSON:
        correlation_name = "Pearson correlation coefficient"
        letter = "r"
    elif kind == CorrelationType.SPEARMAN:
        correlation_name = "Spearman rank correlation coefficient"
        letter = "ρ"
    elif kind == CorrelationType.KENDALL:
        correlation_name = "Kendall rank correlation coefficient"
        letter = "τ"
    elif kind == CorrelationType.PHI:
        correlation_name = "Phi binary correlation coefficient"
        letter = "φ"
    elif kind == CorrelationType.TETRACHORIC:
        correlation_name = "Tetrachoric binary correlation coefficient"
        letter = "ρ<sub>t</sub>"
    else:
        raise ValueError(f"Unknown correlation type: {kind}")

    text = (
        f"A {correlation_name} was calculated to assess the linear relationship between the variables "
        + smart_comma_join([f"'{var}'" for var in columns])
        + f" (Table {TABLE_OR_PLOT_ID_PLACEHOLDER}). "
    )

    if len(columns) == 2:
        return text + get_statement_2_items(
            r=correlation_matrix.loc[columns[1], columns[0]],
            p=p_matrix.loc[columns[1], columns[0]],
            df=df_matrix.loc[columns[1], columns[0]],
            letter=letter,
        )

    if p_matrix.min().min() > 0.05 and not report_non_significant:
        return "No significant correlations were found between the mentioned variables."

    for i_row, row in enumerate(columns):
        for i_column, column in enumerate(columns):
            if i_column < i_row:
                if round(p_matrix.loc[row, column], 3) <= 0.05 or report_non_significant:
                    text += get_statement_multiple_items(
                        r=correlation_matrix.loc[row, column],
                        p=p_matrix.loc[row, column],
                        df=df_matrix.loc[row, column],
                        var1=row,
                        var2=column,
                        id1=id1,
                        id2=id2,
                        id3=id3,
                        letter=letter,
                    )
    return text
