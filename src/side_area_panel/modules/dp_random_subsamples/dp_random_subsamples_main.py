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


import html
import logging
import math
from collections import OrderedDict

import numpy as np
import pandas as pd

from src.common.constant import ColumnType
from src.common.decorators import log_function
from src.data.data import DataColumn
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.common.utility import unique_name
from src.side_area_panel.modules.dp_random_subsamples.dp_random_subsamples_result import RandomSubsamplesResult
from src.side_area_panel.modules.dp_random_subsamples.dp_random_subsamples_ui import Elements


def _parse_count(text):
    try:
        value = float(str(text).strip())
    except ValueError:
        return None
    if not math.isfinite(value) or value < 0 or not value.is_integer():
        return None
    return int(value)


def _parse_percent(text):
    try:
        value = float(str(text).strip().replace(",", "."))
    except ValueError:
        return None
    if not math.isfinite(value) or value < 0:
        return None
    return value


def _aggregate_amounts(rows):
    amounts = OrderedDict()
    order = []
    for label, amount in rows:
        if label not in amounts:
            amounts[label] = 0
            order.append(label)
        amounts[label] += amount
    return amounts, order


def _default_remaining_value(labels):
    integers = []
    for label in labels:
        try:
            number = int(str(label).strip())
        except ValueError:
            continue
        integers.append(number)
    if integers:
        return str(max(integers) + 1)
    return str(len(labels) + 1)


def _largest_remainder_counts(percentages, n):
    raw = [(label, value * n / 100.0) for label, value in percentages.items()]
    floors = OrderedDict((label, int(math.floor(value))) for label, value in raw)
    remainder = n - sum(floors.values())
    fractions = sorted(
        ((value - math.floor(value), index, label) for index, (label, value) in enumerate(raw)),
        key=lambda item: (-item[0], item[1]),
    )
    for _fraction, _index, label in fractions[:remainder]:
        floors[label] += 1
    return floors


def _expanded_labels(counts):
    labels = []
    for label, count in counts.items():
        labels.extend([label] * count)
    return labels


def _format_counts(counts, n, seed):
    parts = [f"{html.escape(str(label))}={count}" for label, count in counts.items() if count > 0]
    return f"Created assignment: {', '.join(parts)} (N={n}). Seed: {seed}."


@log_function
def dp_random_subsamples_main(elements: Elements, result: RandomSubsamplesResult, update):
    cfg = result.config
    data = DATA_MANAGER.get_data_from_data_label(
        data_label=cfg.data_source,
        current_result_id=result.unique_id,
    )
    new_data = data.copy()
    result.data = new_data
    result.error_message = ""
    result.assignment_summary = ""
    result.update_description()

    new_name_raw = (cfg.new_name or "").strip() or "Subsample"
    allocations = cfg.allocations or []
    mode = cfg.assignment_mode or "Counts"
    fill_remaining = True if cfg.fill_remaining is None else bool(cfg.fill_remaining)
    n = new_data.n_rows()

    parsed_rows = []
    for row in allocations:
        if not isinstance(row, dict):
            continue
        label = str(row.get("value", "")).strip()
        amount_text = str(row.get("amount", "")).strip()
        if not label and not amount_text:
            continue
        if not label:
            elements.allocations.set_alert()
            result.error_message = "Enter a value for every allocation row."
            return result
        if mode == "Percentages":
            amount = _parse_percent(amount_text)
            error = "Enter valid non-negative percentages."
        else:
            amount = _parse_count(amount_text)
            error = "Enter valid non-negative integer counts."
        if amount is None:
            elements.allocations.set_alert()
            result.error_message = error
            return result
        parsed_rows.append((label, amount))

    if not parsed_rows:
        elements.allocations.set_alert()
        result.error_message = "Enter at least one allocation value."
        return result

    seed_cfg = cfg.seed if isinstance(cfg.seed, dict) else {}
    # Default to a fixed seed (0) so the assignment is reproducible unless the user sets their own.
    seed = 0
    if seed_cfg.get("use"):
        try:
            seed = int(str(seed_cfg.get("value", "")).strip())
        except ValueError:
            elements.seed.set_alert()
            result.error_message = "Enter a valid integer random seed."
            return result
        if seed < 0:
            elements.seed.set_alert()
            result.error_message = "Enter a non-negative random seed."
            return result

    amounts, value_order = _aggregate_amounts(parsed_rows)
    remaining_value = (cfg.remaining_value or "").strip() or _default_remaining_value(value_order)

    if mode == "Percentages":
        total = sum(amounts.values())
        if total > 100.0 + 1e-9:
            elements.allocations.set_alert()
            result.error_message = "Percentages cannot exceed 100%."
            return result
        if total < 100.0 - 1e-9:
            if not fill_remaining:
                elements.allocations.set_alert()
                result.error_message = "Percentages must sum to 100% when remaining rows are not filled."
                return result
            amounts[remaining_value] = amounts.get(remaining_value, 0.0) + (100.0 - total)
            if remaining_value not in value_order:
                value_order.append(remaining_value)
        counts = _largest_remainder_counts(amounts, n)
    else:
        total = sum(amounts.values())
        if total > n:
            elements.allocations.set_alert()
            result.error_message = "Requested counts cannot exceed the number of rows."
            return result
        if total < n:
            if not fill_remaining:
                elements.allocations.set_alert()
                result.error_message = "Counts must match the number of rows when remaining rows are not filled."
                return result
            amounts[remaining_value] = amounts.get(remaining_value, 0) + (n - total)
            if remaining_value not in value_order:
                value_order.append(remaining_value)
        counts = amounts

    labels = _expanded_labels(counts)
    rng = np.random.default_rng(seed)
    rng.shuffle(labels)

    new_name = unique_name(new_name_raw, set(new_data.column_names()))
    series = pd.Series(labels, name=new_name, dtype="string")
    new_col = DataColumn.initialize_from_series(series)
    new_col.column_type = ColumnType.NOMINAL
    new_col.is_numeric = False
    new_col.column_dtype = "str"
    new_col.order = {label: i + 1 for i, label in enumerate(value_order) if label in counts}
    new_col.automatically_update_order()

    column_names = new_data.column_names()
    if column_names:
        new_data.add_column_after(column_names[-1], new_col)
    else:
        new_data.add_column_first(new_col)

    result.data = new_data
    result.assignment_summary = _format_counts(counts, n, seed)
    result.update_description()
    logging.info("Random sub-samples column %s added", new_name)
    return result
