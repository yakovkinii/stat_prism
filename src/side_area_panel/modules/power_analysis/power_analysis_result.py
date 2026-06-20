#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import attrs

from src.common.translations import t
from src.pyside_ext.markup import HTML
from src.pyside_ext.styling import Style
from src.side_area_panel.modules.common.result.html_result import HTMLTableV2
from src.side_area_panel.modules.common.result.registry import BaseResult

# Test families and what the analysis can solve for. These drive both the UI dropdowns
# and the routing in the main function, so keep the two in sync.
TEST_TYPES = [
    "Two-sample t-test",
    "Paired / one-sample t-test",
    "One-way ANOVA",
    "Correlation",
]
SOLVE_FOR = ["Sample size", "Power", "Effect size"]
TAILS = ["Two-sided", "One-sided"]

# The effect-size symbol shown for each test family.
EFFECT_SYMBOL = {
    "Two-sample t-test": "d",
    "Paired / one-sample t-test": "d",
    "One-way ANOVA": "f",
    "Correlation": "r",
}

_METHODOLOGY = (
    "<b>Power analysis</b><br>"
    "Solves the relationship between significance level (α), statistical power (1 − β), "
    "effect size and sample size for a chosen test, fixing three of them to find the fourth. "
    "t-tests and one-way ANOVA use the standard non-central distributions (statsmodels); "
    "correlation uses the Fisher z approximation. Effect sizes follow Cohen's metrics: "
    "d for t-tests, f for ANOVA, r for correlation."
)


@attrs.define
class PowerAnalysisStudyConfig:
    test_type = attrs.field(default=None)
    solve_for = attrs.field(default=None)
    alpha = attrs.field(default="0.05")
    power = attrs.field(default="0.80")
    effect_size = attrs.field(default="0.5")
    sample_size = attrs.field(default="30")
    n_groups = attrs.field(default="3")
    tails = attrs.field(default=None)


class PowerAnalysisResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: PowerAnalysisStudyConfig):
        super().__init__(unique_id)
        self.unique_id: int = unique_id

        self.title = "Power Analysis"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = PowerAnalysisStudyConfig
        self.config: PowerAnalysisStudyConfig = config
        self.methodology = _METHODOLOGY

        self.needs_update: bool = False
        self.update_description()
        self.set_placeholder()

    def set_placeholder(self, additional_info_html: str = None):
        if additional_info_html is None:
            additional_info_html = t("common.configure_hint_refresh")
        self.result_elements = [
            HTMLTableV2(
                texts=[
                    (
                        self.format_additional_info_html(additional_info_html)
                        + self.format_description_html(self.description)
                    )
                ]
            )
        ]

    def update_description(self):
        self.description = (
            "Estimate the sample size, power, or detectable effect size for a planned study."
            + HTML.hr()
            + HTML.div(_METHODOLOGY, font_size=Style.FontSize.smaller)
        )
