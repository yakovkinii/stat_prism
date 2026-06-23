#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import attrs

from src.data.data import Data
from src.side_area_panel.modules.common.result.registry import BaseResult

# Imputation methods plus the row-removal option, in dropdown order.
IMPUTE_METHODS = ["Mean", "Median", "Mode", "Constant value", "Remove rows"]

_METHODOLOGY = (
    "<b>Impute missing</b><br>"
    "Fills missing cells in the selected columns, or removes rows that have any missing value "
    "in them. <b>Mean</b> / <b>Median</b> use the column's non-missing numeric values; "
    "<b>Mode</b> uses the most frequent value; <b>Constant value</b> fills a value you supply; "
    "<b>Remove rows with missing</b> drops every row that is missing any selected column. "
    "Missing captures both blank strings and NaN."
)


@attrs.define
class ImputeStudyConfig:
    data_source = attrs.field(default=None)
    column_selector = attrs.field(default=None)
    method = attrs.field(default=None)
    constant_value = attrs.field(default=None)


class ImputeResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: ImputeStudyConfig):
        super().__init__(unique_id)
        self.unique_id: int = unique_id
        self.title = "Impute Missing"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = ImputeStudyConfig
        self.config: ImputeStudyConfig = config
        self.needs_update: bool = False
        self.description = ""
        self.methodology = _METHODOLOGY
        self.filled_count = 0
        self.removed_count = 0
        self.update_description()

        self.data = Data([])

    def update_description(self):
        cfg = self.config
        selected = cfg.column_selector[0] if cfg.column_selector else []
        method = cfg.method or "Mean"
        parts = [
            f"Columns ({len(selected)}): " + (", ".join(selected) if selected else "none"),
            f"Method: {method}",
        ]
        if method == "Remove rows":
            parts.append(f"Removed: {self.removed_count} rows")
        else:
            parts.append(f"Filled: {self.filled_count} cells")
        self.description = "<br>".join(parts)
