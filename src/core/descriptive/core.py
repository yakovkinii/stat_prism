import numpy as np
import pandas as pd

from src.common.utility import round_to_significant_digits, smart_comma_join
from src.core.descriptive.descriptive_result import DescriptiveResult
from src.results_panel.results.common.html_element import Cell, HTMLResultElement, HTMLTable, HTMLText, Row


def recalculate_descriptive_study(df: pd.DataFrame, result: DescriptiveResult) -> DescriptiveResult:
    config = result.config
    if len(config.selected_columns) == 0:
        result.result_elements[result.html] = HTMLResultElement()
        return result
    df = df[config.selected_columns]

    # Calculate
    result_n = df.count()
    result_missing = df.isna().sum()
    result_mean = df.mean().apply(lambda x: round_to_significant_digits(x))
    result_minimum = df.min().apply(lambda x: round_to_significant_digits(x))
    result_maximum = df.max().apply(lambda x: round_to_significant_digits(x))
    result_std = df.std().apply(lambda x: round_to_significant_digits(x))

    result_n = result_n if np.any((result_n != df.shape[0])) else None
    result_missing = result_missing if np.any((result_missing != 0)) else None
    result_mean = result_mean
    result_minimum = result_minimum
    result_maximum = result_maximum
    result_std = result_std

    # Table
    full_dict = {
        "N": result_n,
        "Missing": result_missing,
        "Minimum": result_minimum,
        "Maximum": result_maximum,
        "Mean": result_mean,
        "Std. dev.": result_std,
    }

    final_dict = dict()
    for k, v in full_dict.items():
        if v is not None:
            final_dict[k] = v

    df_table = pd.DataFrame(final_dict)
    df_table.index.name = "Variable"
    df_table = df_table.reset_index()
    html_table = HTMLTable([])
    html_table.table_id = "1"
    html_table.table_caption = (
        "Descriptive statistics of " + smart_comma_join([f"'{var}'" for var in df_table.columns]) + "."
    )
    html_table.add_single_row_apa(Row([Cell(x) for x in df_table.columns]))
    for i in range(df_table.shape[0]):
        row = df_table.iloc[i]
        html_table.add_single_row_apa(Row([Cell(row[0])] + [Cell(x) for x in row[1:]]))

    # Verbal
    columns = list(df.columns)
    verbal = verbal_descriptive_keynote(columns, final_dict)

    html_result_element = HTMLResultElement()
    html_result_element.items.append(html_table)
    html_result_element.items.append(HTMLText(verbal))

    result.result_elements[result.html] = html_result_element

    return result


def verbal_descriptive_keynote(columns, final_dict):
    html = ""
    if ("Missing" in final_dict) and ("N" in final_dict):
        data_mis = final_dict["Missing"]
        data_n = final_dict["N"]
        if data_n.min() == 0:
            html += "Variables with N=0 cannot be analysed further. "
        else:
            if (data_mis / data_n).max() < 0.05:
                html += (
                    f"The ratio of missing entries does not surpass "
                    f"{round(np.floor((data_mis/data_n).max()*100))+1}%, and therefore does not significantly"
                    f"distort further analyses. "
                )
            else:
                html += (
                    f"The ratio of missing entries reaches "
                    f"{round(np.floor((data_mis/data_n).max()*100))+1}%, requiring careful further treatment  "
                    f"distort further analyses. "
                )

    if ("Mean" in final_dict) and ("Std. dev." in final_dict):
        data_mean = final_dict["Mean"]
        data_std = final_dict["Std. dev."]

        ratio = data_std / data_mean

        low_rat = []
        high_rat = []
        for col, rat in zip(columns, ratio):
            if rat < 0.2:
                low_rat.append(col)
            if rat > 1:
                high_rat.append(col)

        if len(low_rat) > 0:
            html += (
                "The " + smart_comma_join(low_rat) + " variables are tightly distributed around the mean value, "
                "indicating a strong localization around a non-zero value. "
            )
        if len(high_rat) > 0:
            html += (
                smart_comma_join(high_rat) + " have the standard deviations "
                "comparable to the mean values, indicating a "
                "weakly-localized distribution near the zero value."
            )

        if ("Minimum" in final_dict) and ("Maximum" in final_dict):
            data_min = final_dict["Minimum"]
            data_max = final_dict["Maximum"]
            rang = (data_max - data_min) / 2 / data_std

            high_rang = []
            for col, rng in zip(columns, rang):
                if rng > 3:
                    high_rang.append(col)

            if len(high_rang) > 0:
                html += (
                    smart_comma_join(high_rang) + " have the value ranges exceeding 3 sigma, which indicates either "
                    "an exceptional sample size or the presence of outliers."
                )
            else:
                html += (
                    "All selected variables have their value ranges comparable to the standard deviation, "
                    "indicating internal consistency."
                )
    return html
