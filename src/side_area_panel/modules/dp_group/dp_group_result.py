#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import attrs

from src.data.data import Data
from src.side_area_panel.modules.common.result.registry import BaseResult


@attrs.define
class GroupValuesStudyConfig:
    data_source = attrs.field(default=None)
    column_selector = attrs.field(default=None)
    thresholds = attrs.field(default=None)
    names = attrs.field(default=None)
    new_name = attrs.field(default=None)


class GroupValuesResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: GroupValuesStudyConfig):
        super().__init__(unique_id)
        self.unique_id: int = unique_id
        self.title = "Group Values"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = GroupValuesStudyConfig
        self.config: GroupValuesStudyConfig = config
        self.needs_update: bool = False
        self.description = ""
        self.update_description()

        self.data = Data([])

    def update_description(self):
        cfg = self.config
        selected = cfg.column_selector[0] if cfg.column_selector else []
        column = selected[0] if selected else "(none)"
        parts = [f"Column: {column}"]
        if cfg.thresholds:
            parts.append(f"Split points: {cfg.thresholds}")
        self.description = "<br>".join(parts)
