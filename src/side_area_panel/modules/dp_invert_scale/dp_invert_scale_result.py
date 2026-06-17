#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import attrs

from src.data.data import Data
from src.side_area_panel.modules.common.result.registry import BaseResult


_METHODOLOGY = (
    "<b>Invert scale</b><br>"
    "Reverse-scores the selected columns: each value x becomes (reference &minus; x). With no "
    "reference, it uses (max + min) of the column, so e.g. a 1&ndash;5 Likert item maps 1&harr;5, "
    "2&harr;4, 3&harr;3. Use it to fix reverse-keyed items before building a scale."
)


@attrs.define
class InvertScaleStudyConfig:
    data_source = attrs.field(default=None)
    column_selector = attrs.field(default=None)
    reference = attrs.field(default=None)


class InvertScaleResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: InvertScaleStudyConfig):
        super().__init__(unique_id)
        self.unique_id: int = unique_id
        self.title = "Invert Scale"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = InvertScaleStudyConfig
        self.config: InvertScaleStudyConfig = config
        self.needs_update: bool = False
        self.description = ""
        self.methodology = _METHODOLOGY
        self.update_description()

        self.data = Data([])

    def update_description(self):
        cfg = self.config
        columns = cfg.column_selector[0] if cfg.column_selector else []
        reference = cfg.reference
        reference_text = str(reference) if reference is not None else "max + min (auto)"
        parts = [
            f"Columns ({len(columns)}): " + (", ".join(columns) if columns else "none"),
            f"Inverted as: ({reference_text}) − x",
        ]
        self.description = "<br>".join(parts)
