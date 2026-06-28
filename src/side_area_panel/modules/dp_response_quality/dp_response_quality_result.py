#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import attrs

from src.data.data import Data
from src.side_area_panel.modules.common.cleaning_logic import CHECKS
from src.side_area_panel.modules.common.result.registry import BaseResult


_METHODOLOGY = (
    "<b>Response quality</b><br>"
    "Screens respondents for careless or low-quality answering on the selected questions and "
    "flags them for removal. <b>Duplicate entries</b>: rows that repeat an earlier row. "
    "<b>Long string</b>: the longest run of identical consecutive answers covers at least "
    "<i>Flag at % of items</i> of the questions. <b>High missingness</b>: at least that share of "
    "items is blank. <b>Low variability</b>: the single most-common answer covers at least that "
    "share of items. Flagged rows appear as checkboxes under <b>Remove:</b> (all ticked); untick "
    "any to keep that respondent. Previewing the data shows removed rows in red."
)


@attrs.define
class ResponseQualityStudyConfig:
    data_source = attrs.field(default=None)
    column_selector = attrs.field(default=None)
    check = attrs.field(default=None)
    threshold = attrs.field(default=None)
    remove_list = attrs.field(default=None)
    enabled = attrs.field(default=True)


class ResponseQualityResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: ResponseQualityStudyConfig):
        super().__init__(unique_id)
        self.unique_id: int = unique_id
        self.title = "Response Quality"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = ResponseQualityStudyConfig
        self.config: ResponseQualityStudyConfig = config
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
        check = cfg.check or CHECKS[0]
        parts = [
            f"Questions ({len(selected)}): " + (", ".join(selected) if selected else "none"),
            f"Check: {check}",
        ]
        if check != CHECKS[0]:  # the % threshold is irrelevant to "Duplicate entries"
            parts.append(f"Flag at: {cfg.threshold if cfg.threshold is not None else 50}% of items")
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
