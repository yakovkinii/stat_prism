#  Copyright (c) 2023 StatPrism Team. All rights reserved.
import attrs

from src.data.data import Data
from src.side_area_panel.modules.common.result.registry import BaseResult

_METHODOLOGY = (
    "<b>Bootstrap sensitivity</b><br>"
    "Appends synthetic ('bootstrap') rows to the dataset so you can probe how sensitive a "
    "downstream analysis is to extra observations. The original rows are kept unchanged. For "
    "each selected column you choose the pool of possible values (the existing rows, or a "
    "custom comma-separated list) and how new values are drawn from that pool: "
    "<i>Empirical</i> (resamples the existing values, matching their frequencies), "
    "<i>Uniform</i> (each possible value equally likely), or <i>Normal</i> with a given μ and σ "
    "(ordinal/numeric only; μ and σ default to the column's own mean and SD when left blank). "
    "Columns that are not selected receive empty/NA values in the new rows, and the ID column "
    "gets fresh unique identifiers. Column names, types and colours are never changed; an "
    "ordinal column's category order is rebuilt only when a custom list introduces new values. "
    "Use a fixed random seed to make the generated rows reproducible."
)


@attrs.define
class BootstrapStudyConfig:
    data_source = attrs.field(default=None)
    column_selector = attrs.field(default=None)
    n_rows = attrs.field(default=None)
    seed = attrs.field(default=None)
    column_configs = attrs.field(default=None)


class BootstrapResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: BootstrapStudyConfig):
        super().__init__(unique_id)
        self.unique_id: int = unique_id
        self.title = "Bootstrap Sensitivity"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = BootstrapStudyConfig
        self.config: BootstrapStudyConfig = config
        self.needs_update: bool = False
        self.description = ""
        self.methodology = _METHODOLOGY
        self.update_description()

        self.data = Data([])

    def update_description(self):
        cfg = self.config
        selected = list(cfg.column_selector[0]) if cfg.column_selector else []
        n_rows = cfg.n_rows if cfg.n_rows is not None else 0
        lines = [
            f"Rows to add: {n_rows}",
            f"Seed: {cfg.seed if cfg.seed is not None else 0}",
            f"Bootstrapped columns: {', '.join(selected) if selected else '(none)'}",
        ]
        self.description = "<br>".join(lines)
