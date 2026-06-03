#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import attrs

from src.data.data import Data
from src.side_area_panel.modules.common.result.registry import BaseResult


@attrs.define
class PreprocessStudyConfig:
    data_source = attrs.field(default=None)
    columns = attrs.field(default=None)


class PreprocessResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: PreprocessStudyConfig):
        super().__init__(unique_id)
        self.unique_id: int = unique_id
        self.title = "Preprocess"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = PreprocessStudyConfig
        self.config: PreprocessStudyConfig = config
        self.needs_update: bool = False
        self.description = ""
        self.update_description()

        self.data = Data([])

    def update_description(self):
        specs = self.config.columns or []
        renamed = [s for s in specs if (s.get("new_name") or "").strip()]
        mapped = [s for s in specs if s.get("mapping") and any(f != t for f, t in s["mapping"])]
        ordered = [s for s in specs if s.get("order")]
        parts = [f"Columns: {len(specs)}"]
        if renamed:
            parts.append(f"Renamed: {len(renamed)}")
        if mapped:
            parts.append(f"Mapped: {len(mapped)}")
        if ordered:
            parts.append(f"Reordered: {len(ordered)}")
        self.description = "<br>".join(parts)
