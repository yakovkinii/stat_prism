#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import attrs

from src.data.data import Data
from src.side_area_panel.modules.common.result.registry import BaseResult

_METHODOLOGY = (
    "<b>Formula column</b><br>"
    "Adds a new column computed from an expression over the existing columns, evaluated with "
    "pandas <code>DataFrame.eval</code> (e.g. <code>income / household_size</code> or "
    "<code>pre - post</code>). Reference a column by name; wrap names with spaces in backticks "
    "(e.g. <code>`my col` * 2</code>). If the result is numeric it becomes a numeric column, "
    "otherwise a nominal one."
)


@attrs.define
class FormulaStudyConfig:
    data_source = attrs.field(default=None)
    formula = attrs.field(default=None)
    new_name = attrs.field(default=None)


class FormulaResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: FormulaStudyConfig):
        super().__init__(unique_id)
        self.unique_id: int = unique_id
        self.title = "Formula Column"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = FormulaStudyConfig
        self.config: FormulaStudyConfig = config
        self.needs_update: bool = False
        self.description = ""
        self.methodology = _METHODOLOGY
        self.update_description()

        self.data = Data([])

    def update_description(self):
        cfg = self.config
        name = (cfg.new_name or "").strip() or "(unnamed)"
        formula = (cfg.formula or "").strip() or "(empty)"
        self.description = "<br>".join([f"New column: {name}", f"Formula: {formula}"])
