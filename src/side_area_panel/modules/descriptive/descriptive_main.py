#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import logging

import numpy as np
from scipy import stats

from src.common.constant import ColumnType
from src.common.decorators import log_function
from src.common.translations import t
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.descriptive.descriptive_result import DescriptiveResult
from src.side_area_panel.modules.descriptive.plot import (
    make_box_plot,
    make_distribution_plot,
    make_frequency_bar_plot,
    make_pie_plot,
    make_qq_plot,
)
from src.side_area_panel.modules.descriptive.table import (
    get_frequency_table,
    get_numeric_summary_table,
)


def _fail(result: DescriptiveResult, message: str) -> DescriptiveResult:
    """Show a validation message to the user and log it, then stop."""
    logging.warning("Descriptive: %s", message)
    result.set_error(message)
    return result


def _parse_positive_float(text):
    """Parse a user-entered number; blank / 0 / invalid -> None (i.e. automatic)."""
    try:
        value = float(text)
    except (TypeError, ValueError):
        return None
    return value if value > 0 else None


def _numeric_stats(col, group, series) -> dict:
    data = series.dropna()
    n = int(data.count())
    row = {
        "variable": col,
        "group": group,
        "N": n,
        "missing": int(series.isnull().sum()),
        "mean": data.mean() if n else np.nan,
        "std": data.std() if n > 1 else np.nan,
        "se": data.std() / np.sqrt(n) if n > 1 else np.nan,
        "median": data.median() if n else np.nan,
        "q1": data.quantile(0.25) if n else np.nan,
        "q3": data.quantile(0.75) if n else np.nan,
        "skew": data.skew() if n > 2 else np.nan,
        "kurtosis": data.kurtosis() if n > 3 else np.nan,
        "min": data.min() if n else np.nan,
        "max": data.max() if n else np.nan,
        "shapiro_w": np.nan,
        "shapiro_p": np.nan,
    }
    if n >= 3:
        try:
            row["shapiro_w"], row["shapiro_p"] = stats.shapiro(data)
        except Exception as e:  # pragma: no cover - defensive
            logging.warning("Shapiro-Wilk failed for %s: %s", col, e)
    return row


@log_function
def recalculate_descriptive_study(elements, result: DescriptiveResult) -> DescriptiveResult:
    """Validate inputs, then build the requested summary tables and plots. Unexpected
    exceptions are handled centrally by the panel's recalculate()."""
    cfg = result.config
    result.result_elements = []

    selected_columns = cfg.column_selector[0]
    if not selected_columns:
        return _fail(result, t("descriptive.error.no_variables"))

    grouping = cfg.column_selector[1]
    grouping_column = grouping[0] if grouping else None

    data = DATA_MANAGER.get_data_from_data_label(
        data_label=cfg.data_source,
        current_result_id=result.unique_id,
    )
    columns = selected_columns + ([grouping_column] if grouping_column else [])
    # Ordinal columns are mapped to numeric codes so they get quantitative treatment
    # (summary / distribution / box / Q-Q) -- e.g. Likert scales; nominal stay as labels.
    df = data.get_dataframe(columns=columns, map_ordinal=True)

    numeric_columns = [
        col for col in selected_columns if data[col].column_type in (ColumnType.NUMERIC, ColumnType.ORDINAL)
    ]
    categorical_columns = [col for col in selected_columns if col not in numeric_columns]
    groupby_values = list(df[grouping_column].dropna().unique()) if grouping_column else None

    # ----- Numeric summary table -----
    if numeric_columns:
        rows = []
        for col in numeric_columns:
            if grouping_column is None:
                rows.append(_numeric_stats(col, None, df[col]))
            else:
                for groupby_value in groupby_values:
                    rows.append(_numeric_stats(col, groupby_value, df.loc[df[grouping_column] == groupby_value][col]))
        summary = get_numeric_summary_table(
            rows,
            caption=t("descriptive.table.caption"),
            extended=bool(cfg.extended_stats),
            groupby_column=grouping_column,
        )
        result.update_and_add_element(summary, "descriptive summary")

    # ----- Categorical frequency tables -----
    if cfg.frequency_table:
        for col in categorical_columns:
            value_counts = df[col].value_counts()
            if value_counts.empty:
                continue
            freq = get_frequency_table(
                caption=t("descriptive.freq.caption", col=col),
                value_counts=value_counts.sort_index(),
            )
            result.update_and_add_element(freq, f"descriptive freq {col}")

    # ----- Plots -----
    bin_width = _parse_positive_float(cfg.bin_width)
    kde_smoothing = _parse_positive_float(cfg.kde_smoothing)

    for col in selected_columns:
        if col in numeric_columns:
            if cfg.show_distribution:
                plot = make_distribution_plot(
                    df, col, grouping_column, groupby_values, bin_width, kde_smoothing, bool(cfg.show_kde)
                )
                if plot is not None:
                    result.update_and_add_element(plot, f"descriptive distribution {col}")
            if cfg.show_box:
                plot = make_box_plot(df, col, grouping_column, groupby_values)
                if plot is not None:
                    result.update_and_add_element(plot, f"descriptive box {col}")
            if cfg.show_qq:
                plot = make_qq_plot(df[col], col)
                if plot is not None:
                    result.update_and_add_element(plot, f"descriptive qq {col}")
        else:
            if cfg.show_frequency_bars:
                plot = make_frequency_bar_plot(df[col], col)
                if plot is not None:
                    result.update_and_add_element(plot, f"descriptive frequency {col}")
            if cfg.show_pie:
                plot = make_pie_plot(df[col], col)
                if plot is not None:
                    result.update_and_add_element(plot, f"descriptive pie {col}")

    result.title_context = ", ".join(col[:16] for col in selected_columns)
    if grouping_column:
        result.title_context += "\n" + grouping_column[:16]
    return result
