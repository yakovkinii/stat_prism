#  Copyright (c) 2023 StatPrism Team. All rights reserved.

import logging

import numpy as np
import pandas as pd

from src.common.decorators import log_function
from src.common.qcolor import Colors
from src.side_area_panel.modules.common.result.html_result import Cell, HTMLTableV2, Row
from src.side_area_panel.modules.common.result.plot_result import Bar, BarPlotConfig, PlotV2
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.multiple_response.multiple_response_result import MultipleResponseResult


def _fail(result: MultipleResponseResult, message: str) -> MultipleResponseResult:
    logging.warning("Multiple Response: %s", message)
    result.set_error(message)
    return result


def _pct(numerator, denominator):
    return f"{(100.0 * numerator / denominator):.1f}%" if denominator else "—"


@log_function
def recalculate_multiple_response_study(elements, result: MultipleResponseResult, update) -> MultipleResponseResult:
    cfg = result.config
    result.result_elements = []

    columns = list(cfg.column_selector[0]) if cfg.column_selector and cfg.column_selector[0] else []
    if not columns:
        return _fail(result, "Select the 0/1 indicator columns that make up one multi-select question.")

    data = DATA_MANAGER.get_data_from_data_label(
        data_label=cfg.data_source,
        current_result_id=result.unique_id,
    )
    columns = [c for c in columns if c in data.column_names()]
    if not columns:
        return _fail(result, "The selected columns are not available in this data source.")

    df = data.get_dataframe(columns=columns)
    # Treat any non-zero, non-missing value as "selected".
    selected = pd.DataFrame({c: (pd.to_numeric(df[c], errors="coerce").fillna(0) != 0).astype(int) for c in columns})

    counts = {c: int(selected[c].sum()) for c in columns}
    total_selections = int(sum(counts.values()))
    n_cases = int((selected.sum(axis=1) > 0).sum())  # respondents with >=1 selection

    if total_selections == 0:
        return _fail(result, "No selections found in the chosen columns (all values are 0 or missing).")

    update(50)

    # ----- Table -----
    table = HTMLTableV2(table_caption="Multiple-response frequencies")
    table.add_title_row_apa(
        Row([Cell("Option"), Cell("Selected", center=True), Cell("% of responses", center=True), Cell("% of cases", center=True)])
    )
    for c in columns:
        table.add_single_row_apa(
            Row([
                Cell(str(c)),
                Cell(str(counts[c]), center=True),
                Cell(_pct(counts[c], total_selections), center=True),
                Cell(_pct(counts[c], n_cases), center=True),
            ])
        )
    table.add_single_row_apa(
        Row([
            Cell("Total responses"),
            Cell(str(total_selections), center=True),
            Cell("100.0%", center=True),
            Cell(_pct(total_selections, n_cases), center=True),
        ])
    )
    table.add_text(
        f"Cases = {n_cases} respondent(s) with at least one selection; total selections = {total_selections}. "
        "Percentages of cases sum to more than 100% because a respondent can choose several options."
    )
    result.update_and_add_element(table, "multiple response table")

    # ----- Bar chart (counts per option) -----
    if cfg.show_chart:
        colors = Colors()
        categories = [str(c) for c in columns]
        plot = PlotV2(
            items=[
                Bar(
                    x=np.arange(len(categories)),
                    y=[counts[c] for c in columns],
                    width=0.8,
                    label="Selected",
                    config=BarPlotConfig(color=colors.get_color_list()),
                )
            ],
            title="Multiple-response counts",
            plot_title="Multiple-response counts",
            x_axis_title="",
            y_axis_title="Selected (count)",
            x_axis_items=categories,
        )
        result.update_and_add_element(plot, "multiple response chart")

    update(100)
    result.title_context = ", ".join(str(c)[:16] for c in columns[:3])
    return result
