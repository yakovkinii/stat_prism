#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import attrs

from src.data.data import Data
from src.side_area_panel.modules.common.result.registry import BaseResult

_METHODOLOGY = (
    "<b>Calculate scale</b><br>"
    "Builds a new scale column by aggregating the selected item columns &mdash; <b>Sum</b> or "
    "<b>Mean</b> across the items, per row. Optionally convert the result to <b>Stanine</b> "
    "(1&ndash;9). The source questions can be kept, deleted, or auto-renamed (e.g. "
    "&lsquo;Scale Q1&rsquo;&hellip;). <b>Missing values</b> controls respondents with missing "
    "items: <i>Skip respondent</i> (default) gives no scale value when <i>any</i> item is missing; "
    "<i>Allow up to max %</i> aggregates over the present items as long as the share "
    "of missing items is within <b>Max missing %</b> (0% = complete cases only, 100% = aggregate "
    "over whatever is present). Columns placed in <b>Reverse-score first</b> are flipped "
    "(reverse-keyed, using the same reference as <i>Invert Scale</i>) before being aggregated "
    "with the rest; with <b>Replace reverse-scored columns</b> on, those columns are written "
    "back flipped (renamed &lsquo;&hellip; (flipped)&rsquo; unless the questions are auto-renamed)."
)


@attrs.define
class CalculateScaleStudyConfig:
    data_source = attrs.field(default=None)
    column_selector = attrs.field(default=None)
    flip_reference = attrs.field(default=None)
    replace_flipped = attrs.field(default=None)
    name = attrs.field(default=None)
    method = attrs.field(default=None)
    scale = attrs.field(default=None)
    questions_action = attrs.field(default=None)
    missing_values = attrs.field(default=None)
    missing_threshold = attrs.field(default=None)
    color = attrs.field(default=None)
    questions_color = attrs.field(default=None)


class CalculateScaleResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: CalculateScaleStudyConfig):
        super().__init__(unique_id)
        self.unique_id: int = unique_id
        self.title = "Calculate Scale"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = CalculateScaleStudyConfig
        self.config: CalculateScaleStudyConfig = config
        self.needs_update: bool = False
        self.description = ""
        self.methodology = _METHODOLOGY
        self.update_description()

        self.data = Data([])

    def update_description(self):
        cfg = self.config
        questions = (cfg.column_selector[0] if cfg.column_selector else []) or []
        flipped = (cfg.column_selector[1] if cfg.column_selector and len(cfg.column_selector) > 1 else []) or []
        parts = [
            f"Scale: {cfg.name}" if cfg.name else "Scale: (unnamed)",
            f"Method: {cfg.method or 'Sum'}",
            f"Questions ({len(questions)}): " + (", ".join(questions) if questions else "none"),
        ]
        if flipped:
            parts.append(f"Reverse-scored ({len(flipped)}): " + ", ".join(flipped))
        if cfg.scale and cfg.scale != "None":
            parts.append(f"Normalization: {cfg.scale}")
        missing_mode = cfg.missing_values or "Skip respondent"
        if missing_mode == "Skip respondent":
            parts.append("Missing: skip respondent")
        else:
            parts.append(f"Missing: aggregate up to {cfg.missing_threshold or 0}%")
        action = cfg.questions_action or "Keep"
        if action != "Keep":
            parts.append(f"Used questions: {action.lower()}")
        self.description = "<br>".join(parts)
