#  Copyright (C) 2023-2026  StatPrism Team
#  Balashevych A. K., Petrova N. V., Yakovkin I. I.
#
#  This file is part of StatPrism.
#
#  StatPrism is free software: you can redistribute it and/or modify it under
#  the terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  StatPrism is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with
#  StatPrism.  If not, see <https://www.gnu.org/licenses/>.


import logging

import pandas as pd

from src.common.decorators import log_function
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.common.result.plot_result import PlotV2, RosePlot, RosePlotConfig
from src.side_area_panel.modules.rose_plot.rose_plot_result import RosePlotResult


def _fail(result: RosePlotResult, message: str) -> RosePlotResult:
    logging.warning("Rose Plot: %s", message)
    result.set_error(message)
    return result


def _auto_min(values) -> float:
    low = min(values)
    return 0.0 if low >= 0 else float(low)


def _auto_max(values) -> float:
    high = max(values)
    span = high - _auto_min(values)
    headroom = span * 0.08 if span else (abs(high) * 0.08 or 1.0)
    return float(high + headroom)


def _default_decimals(df, columns) -> str:
    """Default for the value labels: one more decimal place than the raw data carries, since the
    aggregate (notably the mean) adds about one digit of precision. Outside the supported range
    (0-4 places) it falls back to "Off" (the full value)."""
    raw = 0
    for column in columns:
        series = pd.to_numeric(df[column], errors="coerce").dropna()
        for value in series.unique():
            d = 0
            while d < 5 and round(float(value), d) != round(float(value), 5):
                d += 1
            raw = max(raw, d)
        if raw > 3:
            break
    return str(raw + 1) if raw <= 3 else "Off"


def _parse_scale(text, auto: float) -> float:
    if text is None:
        return auto
    stripped = str(text).strip().lower()
    if stripped in ("", "auto"):
        return auto
    try:
        return float(stripped)
    except ValueError:
        return auto


@log_function
def recalculate_rose_plot_study(elements, result: RosePlotResult, update) -> RosePlotResult:
    cfg = result.config
    result.result_elements = []

    columns = list(cfg.column_selector[0]) if cfg.column_selector and cfg.column_selector[0] else []
    if not columns:
        return _fail(result, "Select one or more numeric / ordinal columns.")

    data = DATA_MANAGER.get_data_from_data_label(
        data_label=cfg.data_source,
        current_result_id=result.unique_id,
    )
    columns = [c for c in columns if c in data.column_names()]
    if not columns:
        return _fail(result, "The selected columns are not available in this data source.")

    df = data.get_dataframe(columns=columns)
    aggregator = cfg.aggregator or "Mean"

    values = []
    kept = []
    for column in columns:
        series = pd.to_numeric(df[column], errors="coerce").dropna()
        if series.empty:
            continue
        if aggregator == "Sum":
            values.append(float(series.sum()))
        elif aggregator == "Median":
            values.append(float(series.median()))
        else:
            values.append(float(series.mean()))
        kept.append(column)

    if not kept:
        return _fail(result, "The selected columns have no numeric values to aggregate.")

    update(50)

    scale_min = _parse_scale(cfg.scale_min, _auto_min(values))
    scale_max = _parse_scale(cfg.scale_max, _auto_max(values))
    if scale_max <= scale_min:
        scale_max = scale_min + (abs(scale_min) if scale_min else 1.0)

    plot = PlotV2(
        items=[
            RosePlot(
                values=values,
                names=[str(column) for column in kept],
                scale_min=scale_min,
                scale_max=scale_max,
                config=RosePlotConfig(decimals=_default_decimals(df, kept)),
            )
        ],
        title="Rose plot",
        plot_title="",
    )
    result.update_and_add_element(plot, "rose plot")

    update(100)
    result.title_context = ", ".join(str(column)[:16] for column in kept[:3])
    return result
