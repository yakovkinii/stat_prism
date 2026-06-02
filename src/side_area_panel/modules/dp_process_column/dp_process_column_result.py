#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import attrs

from src.data.data import Data
from src.side_area_panel.modules.common.result.registry import BaseResult


@attrs.define
class ProcessColumnStudyConfig:
    data_source = attrs.field(default=None)
    column_selector = attrs.field(default=None)
    rename = attrs.field(default=None)
    flip = attrs.field(default=None)
    scale = attrs.field(default=None)
    keep_original = attrs.field(default=None)

class ProcessColumnResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: ProcessColumnStudyConfig):
        super().__init__(unique_id)
        self.unique_id: int = unique_id
        self.title = "Process Column"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = ProcessColumnStudyConfig
        self.config: ProcessColumnStudyConfig = config
        self.needs_update: bool = False
        self.description = ""
        self.update_description()

        self.data = Data([])

    def update_description(self):
        cfg = self.config
        selected = cfg.column_selector[0] if cfg.column_selector else []
        column = selected[0] if selected else "(none)"
        parts = [f"Column: {column}"]
        if cfg.rename and cfg.rename.get("rename"):
            parts.append(f"Rename to: {cfg.rename.get('new_name')}")
        if cfg.flip and cfg.flip.get("flip"):
            reference = cfg.flip.get("reference_value")
            parts.append(f"Flip around: {reference if reference is not None else 'max + min (auto)'}")
        if cfg.scale and cfg.scale != "None":
            parts.append(f"Normalization: {cfg.scale}")
        parts.append(f"Keep original: {'yes' if cfg.keep_original else 'no'}")
        self.description = "<br>".join(parts)
