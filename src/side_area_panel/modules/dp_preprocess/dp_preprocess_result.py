#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import attrs

from src.data.data import Data
from src.side_area_panel.modules.common.result.registry import BaseResult

_METHODOLOGY = (
    "<b>Preprocess</b><br>"
    "Per-column cleanup before analysis: rename a column, remap its values (e.g. recode "
    "&lsquo;Yes&rsquo;/&lsquo;No&rsquo; to 1/0, or merge categories), set the category order "
    "for ordinal variables (which drives how categories sort in tables and plots), and remove "
    "columns you don't need (the keep checkbox). Setting a column's type casts it immediately "
    "(after any value mapping): Nominal/Ordinal become text labels, Numeric becomes whole "
    "numbers when possible else decimals; an ordinal column's order is auto-inferred and can be "
    "overridden. If a value can't be parsed as a number the column's card is outlined red."
)


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
        self.methodology = _METHODOLOGY
        self.update_description()

        self.data = Data([])

    def update_description(self):
        specs = self.config.columns or []
        renamed = [s for s in specs if (s.get("new_name") or "").strip()]
        mapped = [s for s in specs if s.get("mapping") and any(f != t for f, t in s["mapping"])]
        ordered = [s for s in specs if s.get("order")]
        removed = [s for s in specs if s.get("remove")]
        parts = [f"Columns: {len(specs)}"]
        if renamed:
            parts.append(f"Renamed: {len(renamed)}")
        if mapped:
            parts.append(f"Mapped: {len(mapped)}")
        if ordered:
            parts.append(f"Reordered: {len(ordered)}")
        if removed:
            parts.append(f"Removed: {len(removed)}")
        self.description = "<br>".join(parts)
