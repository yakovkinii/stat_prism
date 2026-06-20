#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import attrs

from src.data.data import Data
from src.side_area_panel.modules.common.result.registry import BaseResult

_METHODOLOGY = (
    "<b>Transform column</b><br>"
    "Reshapes one selected column <i>in place</i> (the column is replaced, not duplicated). "
    "In order: <b>value mapping</b> (recode specific values); <b>target type</b> "
    "(Nominal / Ordinal / Numeric); for Ordinal an explicit <b>category order</b> and an "
    "optional <b>flip</b> that reverses the scale as (reference − x), with the reference "
    "defaulting to max + min; for Numeric a <b>normalisation</b> "
    "(Z-score, Stanine, Center, Min-max, Log, Rank); and a <b>colour tag</b>. The new name "
    "defaults to the column's current name."
)


@attrs.define
class TransformStudyConfig:
    data_source = attrs.field(default=None)
    column_selector = attrs.field(default=None)
    transform_spec = attrs.field(default=None)


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
        spec = cfg.transform_spec if isinstance(cfg.transform_spec, dict) else {}
        parts = [f"Column: {column}", f"Type: {spec.get('type', '(unchanged)')}"]
        if spec.get("type") == "Numeric" and spec.get("normalize") not in (None, "None"):
            parts.append(f"Normalize: {spec.get('normalize')}")
        if spec.get("type") == "Ordinal" and spec.get("flip"):
            parts.append("Flipped")
        self.description = "<br>".join(parts)
