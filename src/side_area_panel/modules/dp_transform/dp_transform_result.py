#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import attrs

from src.data.data import Data
from src.side_area_panel.modules.common.result.registry import BaseResult

# Numeric transforms, in dropdown order. Each produces a new column.
TRANSFORMS = ["Z-score", "Center", "Min-max", "Log", "Rank", "Flip"]

_METHODOLOGY = (
    "<b>Transform column</b><br>"
    "Creates a new numeric column from one selected column: "
    "<b>Z-score</b> (x − mean)/SD; <b>Center</b> x − mean; <b>Min-max</b> rescale to 0&ndash;1; "
    "<b>Log</b> natural log (non-positive values become missing); <b>Rank</b> ascending ranks "
    "(ties averaged); <b>Flip</b> reverse the scale (max + min − x). The original column is kept; "
    "the result is added next to it."
)


@attrs.define
class TransformStudyConfig:
    data_source = attrs.field(default=None)
    column_selector = attrs.field(default=None)
    transform = attrs.field(default=None)
    new_name = attrs.field(default=None)


class TransformResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: TransformStudyConfig):
        super().__init__(unique_id)
        self.unique_id: int = unique_id
        self.title = "Transform Column"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = TransformStudyConfig
        self.config: TransformStudyConfig = config
        self.needs_update: bool = False
        self.description = ""
        self.methodology = _METHODOLOGY
        self.update_description()

        self.data = Data([])

    def update_description(self):
        cfg = self.config
        selected = cfg.column_selector[0] if cfg.column_selector else []
        column = selected[0] if selected else "(none)"
        parts = [f"Column: {column}", f"Transform: {cfg.transform or 'Z-score'}"]
        self.description = "<br>".join(parts)
