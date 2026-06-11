#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import logging

import numpy as np
from scipy import stats

from src.common.constant import ColumnType
from src.common.decorators import log_function
from src.common.translations import t
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.common.utility import format_value_apa, smart_comma_join
from src.side_area_panel.modules.descriptive.descriptive_result import DescriptiveResult
from src.side_area_panel.modules.descriptive.plot import (
    _outliers,
    make_box_plot,
    make_distribution_plot,
    make_frequency_bar_plot,
    make_pie_plot,
    make_qq_plot,
)
from src.side_area_panel.modules.descriptive.table import (
    get_frequency_table,
    get_grouped_frequency_table,
    get_normality_table,
    get_numeric_summary_table,
)

_KS = "Kolmogorov-Smirnov"


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


def _parse_float_or_none(text):
    """Parse a user-entered number; blank / invalid -> None (0 and negatives allowed)."""
    try:
        return float(text)
    except (TypeError, ValueError):
        return None


def _numeric_stats(col, group, series) -> dict:
    data = series.dropna()
    n = int(data.count())
    return {
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
    }


def _normality_stats(col, group, series, test) -> dict:
    data = series.dropna()
    n = int(data.count())
    statistic, p_value = np.nan, np.nan
    if n >= 3 and data.nunique() > 1:
        try:
            if test == _KS:
                sigma = data.std()
                if sigma > 0:
                    result = stats.kstest(data, "norm", args=(data.mean(), sigma))
                    statistic, p_value = result.statistic, result.pvalue
            else:  # Shapiro-Wilk
                statistic, p_value = stats.shapiro(data)
        except Exception as e:  # pragma: no cover - defensive
            logging.warning("Normality test failed for %s: %s", col, e)
    return {"variable": col, "group": group, "norm_stat": statistic, "norm_p": p_value}


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
    id_selection = cfg.column_selector[2] if len(cfg.column_selector) > 2 else []
    id_column = id_selection[0] if id_selection else None

    data = DATA_MANAGER.get_data_from_data_label(
        data_label=cfg.data_source,
        current_result_id=result.unique_id,
    )
    columns = list(selected_columns)
    for extra in (grouping_column, id_column):
        if extra and extra not in columns:
            columns.append(extra)
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

        # Outlier report, placed directly beneath the main summary table. Each sentence
        # names both the variable and (when grouping is set) the group; finally every
        # outlier's ID is listed comma-separated for easy copying.
        outlier_sentences = []
        all_ids = []
        for col in numeric_columns:
            if grouping_column is None:
                groups_iter = [(None, df)]
            else:
                groups_iter = [(gv, df.loc[df[grouping_column] == gv]) for gv in groupby_values]
            for group_value, subframe in groups_iter:
                outliers = _outliers(subframe, col, id_column)
                if not outliers:
                    continue
                target = col if group_value is None else f"{col} ({group_value})"
                listed = smart_comma_join(
                    [
                        f"{lab} ({format_value_apa(val, 2)})" if id_column is not None else lab
                        for val, lab in outliers
                    ]
                )
                outlier_sentences.append(
                    t("descriptive.outliers.line", target=target, n=len(outliers), items=listed)
                )
                all_ids.extend(lab for val, lab in outliers)
        if outlier_sentences:
            text = "".join(outlier_sentences)
            if id_column is not None and all_ids:
                # The same ID can be an outlier on several variables/groups -- de-duplicate
                # (order-preserving) so each is listed once.
                unique_ids = list(dict.fromkeys(all_ids))
                text += t("descriptive.outliers.id_list", ids=", ".join(unique_ids))
            summary.add_text(text)

        result.update_and_add_element(summary, "descriptive summary")

    # ----- Normality table + verbal report -----
    if cfg.show_normality and numeric_columns:
        test = cfg.normality_test or "Shapiro-Wilk"
        letter = "D" if test == _KS else "W"
        norm_rows = []
        for col in numeric_columns:
            if grouping_column is None:
                norm_rows.append(_normality_stats(col, None, df[col], test))
            else:
                for groupby_value in groupby_values:
                    norm_rows.append(
                        _normality_stats(col, groupby_value, df.loc[df[grouping_column] == groupby_value][col], test)
                    )
        normality = get_normality_table(
            norm_rows,
            caption=t("descriptive.normality.caption", test=test),
            test_name=test,
            statistic_letter=letter,
            groupby_column=grouping_column,
            show_normal_column=bool(cfg.verbal_indicators),
        )
        result.update_and_add_element(normality, "descriptive normality")

    # ----- Categorical frequency tables (split by group when grouping is set) -----
    if cfg.frequency_table:
        for col in categorical_columns:
            # Order categories by the column's defined order (ordinality / custom order)
            # rather than alphabetically.
            def _ordered(vc):
                return vc.reindex(data.ordered_categories(col, list(vc.index)))

            if grouping_column is None:
                value_counts = df[col].value_counts()
                if value_counts.empty:
                    continue
                freq = get_frequency_table(
                    caption=t("descriptive.freq.caption", col=col),
                    value_counts=_ordered(value_counts),
                )
            else:
                group_counts = [
                    (gv, _ordered(df.loc[df[grouping_column] == gv, col].value_counts()))
                    for gv in groupby_values
                ]
                if all(vc.empty for _, vc in group_counts):
                    continue
                freq = get_grouped_frequency_table(
                    caption=t("descriptive.freq.caption", col=col),
                    groupby_column=grouping_column,
                    col=col,
                    group_counts=group_counts,
                )
            result.update_and_add_element(freq, f"descriptive freq {col}")

    # ----- Plots -----
    bin_width = _parse_positive_float(cfg.bin_width)
    bin_reference = _parse_float_or_none(cfg.bin_reference)
    kde_smoothing = _parse_positive_float(cfg.kde_smoothing)

    for col in selected_columns:
        if col in numeric_columns:
            if cfg.show_distribution:
                plot = make_distribution_plot(
                    df, col, grouping_column, groupby_values, bin_width, bin_reference, kde_smoothing, bool(cfg.show_kde)
                )
                if plot is not None:
                    result.update_and_add_element(plot, f"descriptive distribution {col}")
            if cfg.show_box:
                plot = make_box_plot(
                    df, col, grouping_column, groupby_values, id_column=id_column, mark_outliers=bool(cfg.mark_outliers)
                )
                if plot is not None:
                    result.update_and_add_element(plot, f"descriptive box {col}")
            if cfg.show_qq:
                plot = make_qq_plot(df[col], col)
                if plot is not None:
                    result.update_and_add_element(plot, f"descriptive qq {col}")
        else:
            category_order = data.ordered_categories(col, list(df[col].dropna().unique()))
            if cfg.show_frequency_bars:
                plot = make_frequency_bar_plot(df, col, grouping_column, groupby_values, category_order)
                if plot is not None:
                    result.update_and_add_element(plot, f"descriptive frequency {col}")
            if cfg.show_pie:
                plot = make_pie_plot(df[col], col, category_order)
                if plot is not None:
                    result.update_and_add_element(plot, f"descriptive pie {col}")

    result.title_context = ", ".join(col[:16] for col in selected_columns)
    if grouping_column:
        result.title_context += "\n" + grouping_column[:16]
    return result
