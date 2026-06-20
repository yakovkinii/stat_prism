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
    "<br><br>"
    "<b>Correlated bootstrapping.</b> An optional <i>reference</i> (anchor) column is sampled "
    "first and independently. <i>Drivers</i> are then sampled to correlate with the reference, "
    "and the remaining <i>columns</i> to correlate with either the reference or a chosen driver "
    "(each with one target and one coefficient ρ; leave ρ blank or 0, or pick "
    "&lsquo;(independent)&rsquo;, for no correlation). Correlation is induced by a "
    "Gaussian-copula / rank-matching scheme: each column's values are drawn from its own "
    "marginal exactly as above, then reordered to follow a latent normal that is blended toward "
    "the target's latent by ρ. This preserves each column's marginal distribution while inducing "
    "an approximate <i>rank</i> (Spearman-like) correlation that works across numeric, ordinal "
    "and nominal columns. The achieved correlation is therefore approximate, not the exact "
    "Pearson value &mdash; the realized correlations measured on the new rows are reported below."
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
        # Lines describing the realized (achieved) correlations and any infeasibility
        # warnings; populated by the main function after it generates the rows.
        self.realized_lines = []
        self.update_description()

        self.data = Data([])

    def update_description(self):
        cfg = self.config
        selector = cfg.column_selector or []
        regular = list(selector[0]) if len(selector) > 0 and selector[0] else []
        drivers = list(selector[1]) if len(selector) > 1 and selector[1] else []
        reference_list = list(selector[2]) if len(selector) > 2 and selector[2] else []
        reference = reference_list[0] if reference_list else None
        n_rows = cfg.n_rows if cfg.n_rows is not None else 0
        lines = [
            f"Rows to add: {n_rows}",
            f"Seed: {cfg.seed if cfg.seed is not None else 0}",
            f"Reference: {reference if reference else '(none)'}",
            f"Drivers: {', '.join(drivers) if drivers else '(none)'}",
            f"Columns: {', '.join(regular) if regular else '(none)'}",
        ]
        lines.extend(getattr(self, "realized_lines", []) or [])
        self.description = "<br>".join(lines)
