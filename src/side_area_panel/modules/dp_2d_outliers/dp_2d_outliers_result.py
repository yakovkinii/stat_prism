#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import attrs

from src.data.data import Data
from src.side_area_panel.modules.common.result.registry import BaseResult


_METHODOLOGY = (
    "<b>2D outliers</b><br>"
    "Removes multivariate outliers from two columns using the <b>Mahalanobis distance</b> of "
    "each point from the joint centre, with a chi-square cutoff (df = 2) at 95% confidence. "
    "This accounts for the correlation between the two variables, unlike per-column thresholds."
)


@attrs.define
class TwoDOutliersStudyConfig:
    data_source = attrs.field(default=None)
    column_selector = attrs.field(default=None)
    enabled = attrs.field(default=True)


class TwoDOutliersResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: TwoDOutliersStudyConfig):
        super().__init__(unique_id)
        self.unique_id: int = unique_id
        self.title = "2D Outliers"
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

    def update_description(self):
        cfg = self.config
        cols1 = cfg.column_selector[0] if cfg.column_selector else []
        cols2 = cfg.column_selector[1] if cfg.column_selector else []
        col_x = cols1[0] if cols1 else "none"
        col_y = cols2[0] if cols2 else "none"
        parts = [
            f"Columns: {col_x}, {col_y}",
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
