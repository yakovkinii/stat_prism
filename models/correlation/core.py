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

    # Plot
    df_plot = df.iloc[:, 0:2]
    plot_result = PlotResultItem(df_plot, f"Plot (Study #{result_id}):")
    plot_result.x_axis_title = df_plot.columns[0]
    plot_result.y_axis_title = df_plot.columns[1]
    result.items.append(plot_result)

    # Verbal
    # columns = list(df.columns)
    verbal = verbal_correlation(corr)
    # verbal = 'Lorem Ipsum Trololo.'
    result.items.append(TextResultItem(verbal, f"Summary (Study #{result_id})"))

    return result


def verbal_correlation(corr):
    corr_matrix = corr.copy()
    np.fill_diagonal(corr_matrix.values, np.nan)
    mask = np.tril(np.ones(corr_matrix.shape), k=-1).astype(bool)
    lower_triangle_corr = corr_matrix.where(mask).stack()
    high_corr_lower_triangle = lower_triangle_corr

    sorted_high_corr_lower_triangle = high_corr_lower_triangle.sort_values(ascending=False)
    sorted_high_corr_lower_triangle_readable = sorted_high_corr_lower_triangle.reset_index()
    sorted_high_corr_lower_triangle_readable.columns = ["col1", "col2", "cor"]

    any_found = False
    html = ""
    snippets = []
    for i, row in sorted_high_corr_lower_triangle_readable.iterrows():
        if row.cor > 0.8 or row.cor < -0.8:
            snippets.append(f"'{row.col1}' and '{row.col2}' (r={row.cor})")

    if len(snippets) > 0:
        any_found = True
        html += (
            smart_comma_join(snippets) + " show a strong correlation/anticorrelation, "
            "indicating a tight relationship "
            "between the respective variables. "
        )

    snippets = []
    for i, row in sorted_high_corr_lower_triangle_readable.iterrows():
        if 0.8 > row.cor > 0.4 or -0.8 < row.cor < -0.4:
            snippets.append(f"'{row.col1}' and '{row.col2}' (r={row.cor})")

    if len(snippets) > 0:
        any_found = True

        html += smart_comma_join(snippets) + " have a moderate correlation/anticorrelation. "

    html += "Other" if any_found else "All"
    html += " correlations are weak or negligible. "

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

    html += f"Overall, the correlations between the {smart_comma_join(all_columns)} variables are {degree} on average."

    return html
