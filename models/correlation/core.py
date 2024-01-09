import numpy as np
import pandas as pd

from core.objects import PlotResultItem, TableResultItem, TextResultItem
from core.utility import smart_comma_join
from models.correlation.objects import CorrelationResult, CorrelationStudyMetadata


def run_correlation_study(df: pd.DataFrame, metadata: CorrelationStudyMetadata, result_id: int) -> CorrelationResult:
    result = CorrelationResult(result_id=result_id, metadata=metadata)
    result.title = f"Correlation (study #{result_id})"

    if len(metadata.selected_columns) < 2:
        return result
    df = df[metadata.selected_columns]
    corr = df.corr().round(2)
    # Table
    df_table = corr.copy()
    df_table.index.name = "Variable"
    df_table = df_table.reset_index()
    result.items.append(TableResultItem(df_table, f"Table (Study #{result_id}):"))

    readable = get_readable(corr)

    # Plot
    name1 = readable.iloc[0, 0] if readable.iloc[0, 2] > -readable.iloc[-1, 2] else readable.iloc[-1, 0]
    name2 = readable.iloc[0, 1] if readable.iloc[0, 2] > -readable.iloc[-1, 2] else readable.iloc[-1, 1]
    df_plot = df.loc[:, [name1, name2]]
    plot_result = PlotResultItem(df_plot[[name1, name2]], f"Plot (Study #{result_id}):")
    plot_result.x_axis_title = name1
    plot_result.y_axis_title = name2
    result.items.append(plot_result)

    # Verbal
    # columns = list(df.columns)
    verbal = verbal_correlation(readable)
    # verbal = 'Lorem Ipsum Trololo.'
    result.items.append(TextResultItem(verbal, f"Summary (Study #{result_id})"))

    return result


def get_readable(corr):
    corr_matrix = corr.copy()
    np.fill_diagonal(corr_matrix.values, np.nan)
    mask = np.tril(np.ones(corr_matrix.shape), k=-1).astype(bool)
    lower_triangle_corr = corr_matrix.where(mask).stack()
    high_corr_lower_triangle = lower_triangle_corr

    sorted_high_corr_lower_triangle = high_corr_lower_triangle.sort_values(ascending=False)
    sorted_high_corr_lower_triangle_readable = sorted_high_corr_lower_triangle.reset_index()
    sorted_high_corr_lower_triangle_readable.columns = ["col1", "col2", "cor"]
    return sorted_high_corr_lower_triangle_readable


def verbal_correlation(sorted_high_corr_lower_triangle_readable):
    any_found = False
    html = ""
    snippets = []
    for i, row in sorted_high_corr_lower_triangle_readable.iterrows():
        if row.cor > 0.8 or row.cor < -0.8:
            snippets.append(f"'{row.col1}' and '{row.col2}' (r={row.cor})")

    if len(snippets) > 0:
        any_found = True
        html += (
            smart_comma_join(snippets) + " show a strong correlation degree, "
            "indicating a tight relationship "
            "between the respective variables. "
        )

    snippets = []
    for i, row in sorted_high_corr_lower_triangle_readable.iterrows():
        if 0.8 > row.cor > 0.4 or -0.8 < row.cor < -0.4:
            snippets.append(f"'{row.col1}' and '{row.col2}' (r={row.cor})")

    if len(snippets) > 0:
        any_found = True

        html += smart_comma_join(snippets) + " have a moderate degree of correlation. "

    html += (
        "Other correlations are relatively weak. "
        if any_found
        else ("All correlations are weak, indicating no significant " "linear relationship between the variables. ")
    )

    cor_mean = sorted_high_corr_lower_triangle_readable.cor.abs().mean()
    all_columns = sorted_high_corr_lower_triangle_readable.col1.unique()
    if cor_mean > 0.8:
        degree = "very strong"
    elif cor_mean > 0.6:
        degree = "strong"
    elif cor_mean > 0.4:
        degree = "moderate"
    else:
        degree = "weak"

    if any_found:
        html += (
            f"Overall, the correlations between the {smart_comma_join(all_columns)} variables are {degree} on average."
        )

    return html
