#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import attrs

from src.data.data import Data
from src.side_area_panel.modules.common.result.registry import BaseResult

_METHODOLOGY = (
    "<b>Split multi-select</b><br>"
    "Splits a multi-select / &lsquo;checkbox&rsquo; column &mdash; where each cell holds a "
    "delimited list of chosen options (e.g. <i>&ldquo;Instagram, TikTok&rdquo;</i>) &mdash; "
    "into one <b>0/1 indicator column per distinct option</b>. A cell gets 1 for an option it "
    "contains and 0 otherwise; blank cells get 0 for every option. The new columns are numeric, "
    "so each can be summarised (its mean is the proportion who chose that option), correlated, "
    "or used as a regression predictor; together they feed the <b>Multiple-Response</b> table. "
    "The original column is left untouched and the indicators are inserted right after it."
)


@attrs.define
class SplitMultiSelectStudyConfig:
    data_source = attrs.field(default=None)
    column_selector = attrs.field(default=None)
    delimiter = attrs.field(default=None)
    prefix = attrs.field(default=None)


class SplitMultiSelectResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: SplitMultiSelectStudyConfig):
        super().__init__(unique_id)
        self.unique_id: int = unique_id
        self.title = "Split Multi-Select"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = SplitMultiSelectStudyConfig
        self.config: SplitMultiSelectStudyConfig = config
        self.needs_update: bool = False
        self.description = ""
        self.methodology = _METHODOLOGY
        self.update_description()

        self.data = Data([])

    def update_description(self):
        cfg = self.config
        selected = cfg.column_selector[0] if cfg.column_selector else []
        column = selected[0] if selected else "(none)"
        delimiter = (cfg.delimiter or ",").strip() or ","
        parts = [f"Column: {column}", f"Delimiter: '{delimiter}'"]
        self.description = "<br>".join(parts)
