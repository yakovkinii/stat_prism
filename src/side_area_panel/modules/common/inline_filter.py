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


# Per-analysis inline filters. An analysis owns a list of Filter configs (result.inline_filters);
# they are NOT chain members. They combine as a logical AND -- a row survives only if it passes
# every filter, each evaluated against the analysis's base input -- and are applied transparently
# when the analysis resolves its data (see DataManager.get_data_from_data_label).

from src.side_area_panel.modules.dp_filter.dp_filter_result import FilterDataStudyConfig
from src.side_area_panel.modules.dp_filter.filter_logic import (
    apply_mask,
    compute_keep_mask,
    filter_target_column,
    removed_positions,
)


def get_inline_filters(result):
    """The analysis's inline-filter list, lazily created (older projects predate the field)."""
    filters = getattr(result, "inline_filters", None)
    if filters is None:
        filters = []
        result.inline_filters = filters
    return filters


def new_inline_filter(data_source) -> FilterDataStudyConfig:
    """A fresh, unconfigured inline filter pinned to the analysis's data source."""
    return FilterDataStudyConfig(
        data_source=data_source,
        column_selector=[[]],
        column_filter=None,
        enabled=True,
    )


def _keep_masks(base_data, filters):
    """The non-trivial keep-masks (skips no-op / broken filters)."""
    masks = []
    names = set(base_data.column_names())
    for cfg in filters:
        column = filter_target_column(cfg)
        if column is not None and column not in names:
            continue  # broken column: excluded here, surfaced separately as an error
        mask, _error, _alert = compute_keep_mask(base_data, cfg)
        if mask is not None:
            masks.append(mask)
    return masks


def combined_keep_mask(base_data, filters):
    """AND of every filter's keep-mask over the base data, or None when nothing filters."""
    masks = _keep_masks(base_data, filters)
    if not masks:
        return None
    combined = masks[0]
    for mask in masks[1:]:
        combined = combined & mask
    return combined


def apply_inline_filters(base_data, filters):
    """Base data with the combined inline filter applied (a copy; unchanged when nothing filters)."""
    return apply_mask(base_data, combined_keep_mask(base_data, filters))


def filter_removed_positions(base_data, cfg) -> list:
    """Row positions one filter removes on its own, measured against the base data (for its card
    row's 'Rows removed' count and the eye preview's red rows)."""
    if filter_target_column(cfg) not in set(base_data.column_names()):
        return []
    mask, _error, _alert = compute_keep_mask(base_data, cfg)
    return removed_positions(mask)


def describe_filter(config) -> str:
    """A short one-line description of a filter, e.g. 'age >= 18' or 'group: A, B'."""
    column = filter_target_column(config)
    if column is None:
        return "(no column)"
    spec = config.column_filter
    if not spec or spec.get("column") != column:
        return column
    if spec.get("mode") == "numeric":
        operation = spec.get("operation")
        if operation in ("is empty", "is not empty"):
            return f"{column} {operation}"
        value = spec.get("value")
        if value not in (None, ""):
            return f"{column} {operation} {value}"
        return column
    if spec.get("mode") == "categorical":
        kept = spec.get("kept_values")
        if kept:
            return f"{column}: " + ", ".join(str(v) for v in kept)
    return column


def broken_filter_indices(base_data, filters) -> list:
    """Indices of filters whose target column is no longer in the data (renamed/removed)."""
    names = set(base_data.column_names())
    broken = []
    for index, cfg in enumerate(filters):
        column = filter_target_column(cfg)
        if column is not None and column not in names:
            broken.append(index)
    return broken
