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


from src.common.decorators import log_function
from src.data.data import OrdinalCastError
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.common.outlier_logic import detect_nd_outliers
from src.side_area_panel.modules.common.removal import clear_removal, finalize_removal
from src.side_area_panel.modules.common.utility import ordinal_cast_error_message, ordinal_numeric_cast_warning
from src.side_area_panel.modules.dp_2d_outliers.dp_2d_outliers_result import TwoDOutliersResult
from src.side_area_panel.modules.dp_2d_outliers.dp_2d_outliers_ui import Elements


@log_function
def dp_2d_outliers_main(elements: Elements, result: TwoDOutliersResult, update):
    """Flag multivariate (N-dimensional) outliers across the selected columns using the
    Mahalanobis distance of each row from the joint centre, with a chi-square cutoff
    (df = number of columns) at 95% confidence. This accounts for the correlations between
    the columns, unlike per-column thresholds. Needs at least two columns."""
    cfg = result.config
    data = DATA_MANAGER.get_data_from_data_label(
        data_label=cfg.data_source,
        current_result_id=result.unique_id,
    )
    result.warnings = []

    if not cfg.enabled:
        return clear_removal(result, data)  # disabled -> no-op, stays in chain

    selected = cfg.column_selector[0] if cfg.column_selector else None
    if not selected or len(selected) < 2:
        # ND outliers are undefined for a single column -> flag the input.
        elements.column_selector.set_alert(0)
        return clear_removal(result, data, "Select two or more columns.")

    # Mahalanobis outliers are numeric: ordinals are used via their face values (error on non-numeric
    # categories, warn that they were cast).
    columns = [c for c in selected if c in data.column_names()]
    try:
        _, cast = data.get_numeric_face_dataframe(columns)
    except OrdinalCastError as error:
        elements.column_selector.set_alert(0)
        return clear_removal(result, data, ordinal_cast_error_message(error.column_name))
    if cast:
        result.set_warning(ordinal_numeric_cast_warning(cast))

    candidates = detect_nd_outliers(data, columns)
    return finalize_removal(result, data, candidates, cfg.remove_list)
