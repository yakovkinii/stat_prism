#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import attrs

from src.common.translations import t
from src.pyside_ext.markup import HTML
from src.pyside_ext.styling import Style
from src.side_area_panel.modules.common.result.registry import BaseResult


@attrs.define
class RegressionStudyConfig:
    data_source = attrs.field(default=None)
    column_selector = attrs.field(default=None)
    standardized = attrs.field(default=None)
    verbal_indicators = attrs.field(default=None)
    diagnostics = attrs.field(default=None)
    plots = attrs.field(default=None)


# Fine-print on the exact methodology / variants this module uses. English only by
# design (only reports/tables are localised), rendered in a smaller font under the
# general description so the chosen conventions are explicit and auditable.
_ASSUMPTIONS_FINE_PRINT_EN = (
    "<b>Methodology &amp; assumptions</b>"
    "<ul>"
    "<li><b>Estimator.</b> Ordinary least squares (statsmodels OLS) with an intercept. Rows "
    "with any missing value in the used columns are dropped (list-wise).</li>"
    "<li><b>Model fit.</b> R&sup2; and adjusted R&sup2;, plus the overall F-test "
    "(F, its two degrees of freedom and p) and the sample size N.</li>"
    "<li><b>Coefficients.</b> Unstandardised B with its standard error (SE), the standardised "
    "coefficient &beta;, the t statistic and its p-value.</li>"
    "<li><b>Table symbols.</b> <b>N</b> sample size (complete rows); <b>R&sup2;</b> share of "
    "the outcome's variance explained; <b>adjusted R&sup2;</b> the same, penalised for the "
    "number of predictors; <b>F</b> the overall model test statistic with degrees of freedom "
    "<b>df</b> = (predictors, residual); <b>B</b> the unstandardised coefficient (expected "
    "change in the outcome per one-unit increase in the predictor, holding the others "
    "constant); <b>SE</b> its standard error; <b>&beta;</b> the standardised coefficient "
    "(B rescaled by SD(predictor)/SD(outcome), so predictors are comparable on a common "
    "scale; blank for the intercept); <b>t</b> = B/SE, the statistic testing the coefficient; "
    "<b>p</b> its two-sided p-value.</li>"
    "<li><b>Significance.</b> A coefficient (or the overall F-test) is &lsquo;significant&rsquo; "
    "when p &lt; .05 &mdash; i.e. the association is unlikely (&lt; 5% under the null) to be "
    "zero in the population, given the other predictors. It speaks to reliability of the sign, "
    "not to the size or practical importance of the effect.</li>"
    "<li><b>Moderation.</b> Adds the moderator and its product with each predictor "
    "(predictor &times; moderator); a significant interaction indicates moderation. The plot "
    "shows simple slopes at &minus;1 SD, mean and +1 SD of the moderator.</li>"
    "<li><b>Mediation.</b> Estimates the predictor&rarr;mediator path and the "
    "predictor/mediator&rarr;outcome paths (a separate Path-estimates table); the plot "
    "contrasts the direct and total effects.</li>"
    "<li><b>Verbal indicators.</b> &lsquo;Verbal indicators in tables&rsquo; adds a "
    "Significant? column next to each p-value (&alpha; = .05).</li>"
    "<li><b>Diagnostics.</b> Optional. <b>VIF</b> (variance inflation factor) flags "
    "multicollinearity among predictors: &gt; 5 moderate, &gt; 10 high (interaction terms in a "
    "moderation model inflate VIF by construction &mdash; centring the predictors reduces it). "
    "<b>Residuals vs fitted</b> should show a flat, structureless band &mdash; a funnel suggests "
    "heteroscedasticity, a curve suggests non-linearity. The <b>normal Q-Q</b> of residuals "
    "should track the reference line; systematic departures indicate non-normal residuals.</li>"
    "<li><b>Assumptions (not checked here).</b> OLS assumes a roughly linear relationship, "
    "independent and constant-variance (homoscedastic) errors, and &mdash; for exact small-"
    "sample inference &mdash; approximately normal residuals. These are not tested in this "
    "module; inspect residuals / use judgement if in doubt.</li>"
    "<li><b>Threshold.</b> Tests are two-sided and use &alpha; = .05.</li>"
    "</ul>"
)


class RegressionResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: RegressionStudyConfig):
        super().__init__(unique_id)
        # Unique integer id, not for display
        self.unique_id: int = unique_id

        self.title = "Regression"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = RegressionStudyConfig
        self.config: RegressionStudyConfig = config

        self.needs_update: bool = False
        self.update_description()
        self.set_placeholder()

    def update_description(self):
        # General guide is localised; the methodology fine-print is English-only and
        # rendered smaller, separated by a rule.
        self.description = (
            t("regression.description")
            + HTML.hr()
            + HTML.div(_ASSUMPTIONS_FINE_PRINT_EN, font_size=Style.FontSize.smaller)
        )
