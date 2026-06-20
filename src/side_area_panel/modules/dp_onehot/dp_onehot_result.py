#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import attrs

from src.data.data import Data
from src.side_area_panel.modules.common.result.registry import BaseResult

_METHODOLOGY = (
    "<b>Encode categories (one-hot)</b><br>"
    "Turns a single-select nominal column with k categories into <b>0/1 indicator columns</b> "
    "(one per category, named <i>column = category</i>). This lets a categorical variable be "
    "used as a <b>regression predictor</b> &mdash; the regression input accepts only numeric / "
    "ordinal columns, so a nominal must be encoded first. With <b>Drop reference category</b> on "
    "(default), one category is omitted (k&minus;1 columns) and becomes the baseline each "
    "indicator&rsquo;s coefficient is compared against &mdash; the usual setup for regression "
    "(it avoids the redundant, collinear k-th column). Leave it off to keep all k columns "
    "(useful for plain description). A row with a missing value gets 0 in every indicator. The "
    "original column is left untouched and the indicators are inserted right after it."
)


@attrs.define
class OneHotStudyConfig:
    data_source = attrs.field(default=None)
    column_selector = attrs.field(default=None)
    drop_reference = attrs.field(default=None)
    reference = attrs.field(default=None)


class OneHotResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: OneHotStudyConfig):
        super().__init__(unique_id)
        self.unique_id: int = unique_id
        self.title = "Encode Categories"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = OneHotStudyConfig
        self.config: OneHotStudyConfig = config
        self.needs_update: bool = False
        self.description = ""
        self.methodology = _METHODOLOGY
        self.update_description()

        self.data = Data([])

    def update_description(self):
        cfg = self.config
        selected = cfg.column_selector[0] if cfg.column_selector else []
        column = selected[0] if selected else "(none)"
        parts = [f"Column: {column}"]
        # drop_reference defaults to True (checkbox default state) when unset.
        drop = cfg.drop_reference if cfg.drop_reference is not None else True
        if drop:
            ref = (cfg.reference or "").strip()
            parts.append(f"Reference dropped: {ref if ref else '(first category)'}")
        else:
            parts.append("Reference dropped: no (all categories)")
        self.description = "<br>".join(parts)
