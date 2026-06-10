#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import attrs

from src.common.translations import t
from src.pyside_ext.markup import HTML
from src.pyside_ext.styling import Style
from src.side_area_panel.modules.common.result.registry import BaseResult


@attrs.define
class DescriptiveStudyConfig:
    data_source = attrs.field(default=None)
    column_selector = attrs.field(default=None)
    # Tables
    extended_stats = attrs.field(default=None)
    frequency_table = attrs.field(default=None)
    # Plots
    show_distribution = attrs.field(default=None)
    show_box = attrs.field(default=None)
    show_frequency_bars = attrs.field(default=None)
    show_pie = attrs.field(default=None)
    show_qq = attrs.field(default=None)
    # Distribution-plot controls
    show_kde = attrs.field(default=None)
    bin_width = attrs.field(default=None)
    kde_smoothing = attrs.field(default=None)


# Fine-print on the exact methodology / variants this module uses. English only by
# design (only reports/tables are localised), rendered in a smaller font under the
# general description so the chosen conventions are explicit and auditable.
_ASSUMPTIONS_FINE_PRINT_EN = (
    "<b>Methodology &amp; assumptions</b>"
    "<ul>"
    "<li><b>Numeric summary.</b> N, missing, mean, SD, min and max; optionally (Extended "
    "stats) median, Q1/Q3 (IQR), the standard error of the mean, and skewness &amp; "
    "kurtosis (Fisher / excess, so a normal distribution has 0).</li>"
    "<li><b>Normality.</b> Shapiro&ndash;Wilk W with its p (needs N &ge; 3).</li>"
    "<li><b>Categorical summary.</b> A per-variable frequency table with counts and "
    "percentages (of non-missing) is shown for non-numeric variables.</li>"
    "<li><b>Histograms.</b> Densities. Bin width is automatic (Freedman&ndash;Diaconis / "
    "&lsquo;auto&rsquo;) unless a Bin width is given &mdash; set it to 1 for Likert-type "
    "scales so each value is its own bar.</li>"
    "<li><b>KDE.</b> Gaussian kernel, Scott&rsquo;s-rule bandwidth multiplied by the KDE "
    "smoothing factor (1 = default; raise it to avoid a spiky curve on discrete/Likert "
    "data).</li>"
    "<li><b>Box plots.</b> Tukey boxes (median, IQR, 1.5&times;IQR whiskers) with outliers "
    "drawn as points. Computed on non-missing values.</li>"
    "<li><b>Q-Q plots.</b> Sample quantiles vs theoretical normal quantiles, with a "
    "reference line.</li>"
    "<li><b>Grouping.</b> A grouping column splits the numeric summary, distribution plots "
    "and box plots by group. Frequency tables/bars, pie and Q-Q plots always use the whole "
    "variable.</li>"
    "<li><b>Missing data.</b> Each variable is summarised/plotted on its own non-missing "
    "values.</li>"
    "</ul>"
)


class DescriptiveResult(BaseResult):
    def __init__(self, unique_id, settings_panel_index, config: DescriptiveStudyConfig):
        super().__init__(unique_id)
        # Unique integer id, not for display
        self.unique_id: int = unique_id

        self.title = "Descriptive Statistics"
        self.title_context = ""
        self.settings_panel_index = settings_panel_index
        self.config_class = DescriptiveStudyConfig
        self.config: DescriptiveStudyConfig = config

        self.needs_update: bool = False
        self.update_description()
        self.set_placeholder()

    def update_description(self):
        # General guide is localised; the methodology fine-print is English-only and
        # rendered smaller, separated by a rule.
        self.description = (
            t("descriptive.description")
            + HTML.hr()
            + HTML.div(_ASSUMPTIONS_FINE_PRINT_EN, font_size=Style.FontSize.smaller)
        )
