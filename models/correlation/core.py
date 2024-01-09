import numpy as np
import pandas as pd

from core.objects import TableResultItem, TextResultItem, PlotResultItem
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
    threshold=0.9
    high_corr_lower_triangle = lower_triangle_corr[lower_triangle_corr > threshold]

    sorted_high_corr_lower_triangle = high_corr_lower_triangle.sort_values(ascending=False)
    sorted_high_corr_lower_triangle_readable = sorted_high_corr_lower_triangle.reset_index()
    sorted_high_corr_lower_triangle_readable.columns = ['Column1', 'Column2', 'Correlation']

    html=f'No correlations larger than {threshold} found.'
    snippets = []
    for i, row in sorted_high_corr_lower_triangle_readable.iterrows():
        snippets.append(f"'{row.Column1}' and '{row.Column2}' (r={row.Correlation})")
    if len(snippets)>0:
        html='Largest correlations were found between ' + smart_comma_join(snippets)+'.'
    return html
