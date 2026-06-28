#  Copyright (c) 2023 StatPrism Team. All rights reserved.
"""Shared helpers for "row-removal" data-processing steps (outliers, data cleaning).

These steps all follow the same pattern: a detector proposes a list of candidate row
IDs to remove, the user can keep some of them (via the Remove-list checkboxes), and the
step then drops the remaining ones while recording everything the data-preview popup
needs to show the removed rows in red (``full_data`` + ``removed_positions``), exactly
like the Filter step.
"""

from src.data.data import Data


def ids_for_mask(data: Data, mask) -> list:
    """The ID values of the rows where ``mask`` is True, as plain Python scalars."""
    ids = data.get_id_series()[mask]
    return [v.item() if hasattr(v, "item") else v for v in ids]


def clear_removal(result, data: Data, message: str = ""):
    """No-op / disabled / invalid-input path: keep every row and reset the preview
    bookkeeping. ``message`` (if given) is shown red in the card's short summary."""
    result.data = data.copy()
    result.full_data = Data([])
    result.removed_positions = []
    result.removed_ids = []
    result.removed_count = 0
    result.error_message = message
    return result


def finalize_removal(result, data: Data, candidate_ids, kept_ids):
    """Drop ``candidate_ids`` except the ones the user kept (``kept_ids``).

    Records ``full_data`` (the unfiltered data) and ``removed_positions`` (positions of
    the dropped rows in that unfiltered order) so the preview popup can render them red,
    plus ``removed_ids`` / ``removed_count`` for the card description.
    """
    kept_set = set(kept_ids or [])
    removed_ids = [i for i in candidate_ids if i not in kept_set]

    new_data = data.copy()
    id_series = new_data.get_id_series()
    mask_removed = id_series.isin(removed_ids)

    result.full_data = data.copy()
    result.removed_positions = [i for i, removed in enumerate(mask_removed.tolist()) if removed]

    keep = ~mask_removed
    for column in new_data.columns:
        column.data_series = column.data_series[keep]

    result.removed_ids = removed_ids
    result.removed_count = len(removed_ids)
    result.data = new_data
    result.error_message = ""
    return result
