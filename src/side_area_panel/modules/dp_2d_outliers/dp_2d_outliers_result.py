#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import attrs

from src.data.data import Data
from src.side_area_panel.modules.common.result.registry import BaseResult

_METHODOLOGY = (
    "<b>ND outliers</b><br>"
    "Flags multivariate (N-dimensional) outliers across the selected columns using the "
    "<b>Mahalanobis distance</b> of each row from the joint centre, with a chi-square cutoff "
    "(df = number of columns) at 95% confidence. This accounts for the correlations between the "
    "columns, unlike per-column thresholds. Select two or more columns. Flagged rows appear as "
    "checkboxes under <b>Remove:</b> (all ticked); untick any to keep that respondent. Previewing "
    "the data shows removed rows in red."
)


@attrs.define
class TwoDOutliersStudyConfig:
    data_source = attrs.field(default=None)
    column_selector = attrs.field(default=None)
    remove_list = attrs.field(default=None)
    enabled = attrs.field(default=True)


class TwoDOutliersResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: TwoDOutliersStudyConfig):
        super().__init__(unique_id)
        self.unique_id: int = unique_id
        self.title = "ND Outliers"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = TwoDOutliersStudyConfig
        self.config: TwoDOutliersStudyConfig = config
        self.needs_update: bool = False
        self.toggleable: bool = True
        self.removed_count: int = 0
        self.removed_ids: list = []
        self.description = ""
        self.methodology = _METHODOLOGY
        self.update_description()

        self.data = Data([])
        # Unfiltered data + removed positions for the red-row data preview (as in Filter).
        self.full_data = Data([])
        self.removed_positions = []

    def update_description(self):
        cfg = self.config
        selected = cfg.column_selector[0] if cfg.column_selector else []
        parts = [
            f"Columns ({len(selected)}): " + (", ".join(selected) if selected else "none"),
            "Criterion: Mahalanobis distance (95%)",
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
