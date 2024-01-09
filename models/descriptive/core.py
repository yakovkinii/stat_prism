import pandas as pd

from core.objects import TableResultItem, TextResultItem
from core.utility import num_to_str, smart_comma_join, round_to_significant_digits
from models.descriptive.objects import DescriptiveResult, DescriptiveStudyMetadata


def run_descriptive_study(df: pd.DataFrame, metadata: DescriptiveStudyMetadata, result_id: int) -> DescriptiveResult:
    result = DescriptiveResult(result_id=result_id, metadata=metadata)
    result.title = f"Descriptive statistics (study #{result_id})"

    if len(metadata.selected_columns) == 0:
        return result
    df = df[metadata.selected_columns]

    # Calculate
    result_n = df.count() if metadata.n else None
    result_missing = df.isna().sum() if metadata.missing else None
    result_mean = df.mean().apply(lambda x: round_to_significant_digits(x)) if metadata.mean else None
    result_median = df.median().apply(lambda x: round_to_significant_digits(x)) if metadata.median else None
    result_minimum = df.min().apply(lambda x: round_to_significant_digits(x)) if metadata.minimum else None
    result_maximum = df.max().apply(lambda x: round_to_significant_digits(x)) if metadata.maximum else None
    result_std = df.std().apply(lambda x: round_to_significant_digits(x)) if metadata.stddev else None
    result_var = df.var().apply(lambda x: round_to_significant_digits(x)) if metadata.variance else None

    # Table
    full_dict = {
        "N": result_n,
        "Missing": result_missing,
        "Mean": result_mean,
        "Median": result_median,
        "Minimum": result_minimum,
        "Maximum": result_maximum,
        "Std. dev.": result_std,
        "Variance": result_var,
    }
    final_dict = dict()
    for k, v in full_dict.items():
        if v is not None:
            final_dict[k] = v

    if len(final_dict) > 0:
        df_table = pd.DataFrame(final_dict)
        df_table.index.name = "Variable"
        df_table = df_table.reset_index()
        result.items.append(TableResultItem(df_table, f"Table (Study #{result_id}):"))

    # Verbal
    columns = list(df.columns)
    verbal = verbal_descriptive(columns, result_n, result_mean, result_minimum, result_maximum)
    result.items.append(TextResultItem(verbal, f"Summary (Study #{result_id})"))
    return result


def verbal_descriptive(columns, result_n, result_mean, result_minimum, result_maximum):
    html = ""
    # 1. Aggregate
    if result_n is not None and result_n.nunique() == 1:
        html += smart_comma_join([f"'{c}'" for c in columns]) + f" had {result_n.iloc[0]:} entries. "
    else:
        ...

    # 2. Individual
    ind_htmls = []
    for c in columns:
        snippets = []
        if result_minimum is not None and result_maximum is not None:
            snippets.append(f"ranged from {result_minimum[c]} to {result_maximum[c]}")
        if result_mean is not None:
            snippets.append(f"had the mean value of {result_mean[c]}")
        if len(snippets) > 0:
            ind_htmls.append(f"'{c}'" + " " + smart_comma_join(snippets))
    html += smart_comma_join(ind_htmls)
    return html
