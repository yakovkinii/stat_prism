#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import attrs

from src.data.data import Data
from src.side_area_panel.modules.common.result.registry import BaseResult


_METHODOLOGY = (
    "<b>Outliers</b><br>"
    "Flags rows whose value on <i>any</i> selected column is an outlier. "
    "<b>IQR</b>: outside Q1 &minus; 1.5&times;IQR .. Q3 + 1.5&times;IQR. "
    "<b>Z-score</b>: |z| &gt; 3. Flagged rows are listed as checkboxes under <b>Remove:</b> "
    "(all ticked); untick any to keep that respondent. Previewing the data shows the removed "
    "rows in red. Toggle the step off (card button) to keep all rows."
)


@attrs.define
class OutliersStudyConfig:
    data_source = attrs.field(default=None)
    column_selector = attrs.field(default=None)
    method = attrs.field(default=None)
    remove_list = attrs.field(default=None)
    enabled = attrs.field(default=True)


class OutliersResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: OutliersStudyConfig):
        super().__init__(unique_id)
        self.unique_id: int = unique_id
        self.title = "Outliers"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = OutliersStudyConfig
        self.config: OutliersStudyConfig = config
        self.needs_update: bool = False
        self.toggleable: bool = True
        self.removed_count: int = 0
        self.removed_ids: list = []
        self.description = ""
        self.methodology = _METHODOLOGY
        self.update_description()

        self.data = Data([])
        # For the data-preview popup: the unfiltered data plus the removed row positions,
        # so removed rows can be shown in red (as in Filter).
        self.full_data = Data([])
        self.removed_positions = []

    def update_description(self):
        cfg = self.config
        selected = cfg.column_selector[0] if cfg.column_selector else []
        parts = [
            f"Columns ({len(selected)}): " + (", ".join(selected) if selected else "none"),
            f"Method: {cfg.method or 'IQR'}",
        ]
        if cfg.enabled:
            parts.append(f"Removed: {self.removed_count} rows")
            if self.removed_ids:
                shown = ", ".join(str(i) for i in self.removed_ids[:20])
                if len(self.removed_ids) > 20:
                    shown += ", …"
                parts.append(f"Removed IDs: {shown}")
        else:
            parts.append("Status: disabled")
        self.description = "<br>".join(parts)
