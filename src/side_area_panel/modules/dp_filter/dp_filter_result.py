#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import attrs

from src.data.data import Data
from src.side_area_panel.modules.common.result.registry import BaseResult


@attrs.define
class FilterDataStudyConfig:
    data_source = attrs.field(default=None)
    column_selector = attrs.field(default=None)
    column_filter = attrs.field(default=None)
    enabled = attrs.field(default=True)


class FilterDataResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: FilterDataStudyConfig):
        super().__init__(unique_id)
        self.unique_id: int = unique_id
        self.title = "Filter"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = FilterDataStudyConfig
        self.config: FilterDataStudyConfig = config
        self.needs_update: bool = False
        # Tells the result card to show the large enable/disable toggle.
        self.toggleable: bool = True
        self.description = ""
        self.update_description()

        self.data = Data([])

    def update_description(self):
        cfg = self.config
        selected = cfg.column_selector[0] if cfg.column_selector else []
        column = selected[0] if selected else "(none)"
        parts = [f"Column: {column}"]

        spec = cfg.column_filter
        if spec and spec.get("column") == column:
            if spec.get("mode") == "numeric":
                value = spec.get("value")
                if value not in (None, ""):
                    parts.append(f"Keep where {column} {spec.get('operation')} {value}")
            elif spec.get("mode") == "categorical":
                kept = spec.get("kept_values")
                if kept is not None:
                    parts.append("Keep values: " + (", ".join(str(v) for v in kept) if kept else "(none)"))

        parts.append("Status: enabled" if cfg.enabled else "Status: disabled")
        self.description = "<br>".join(parts)
