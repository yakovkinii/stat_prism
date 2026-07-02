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
    show_normality = attrs.field(default=None)
    normality_test = attrs.field(default=None)
    verbal_indicators = attrs.field(default=None)  # in-table verbal columns (e.g. "Normal?")
    interpretation = attrs.field(default=None)  # plain-language sentences: detail level (prose dropdown)
    number_columns = attrs.field(default=None)
    # Plots
    show_distribution = attrs.field(default=None)
    show_box = attrs.field(default=None)
    mark_outliers = attrs.field(default=None)
    show_frequency_bars = attrs.field(default=None)
    show_pie = attrs.field(default=None)
    show_qq = attrs.field(default=None)
    # Distribution-plot controls
    show_kde = attrs.field(default=None)
    bin_width = attrs.field(default=None)
    bin_reference = attrs.field(default=None)
    kde_smoothing = attrs.field(default=None)


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
            + HTML.div(t("descriptive.fine_print"), font_size=Style.FontSize.smaller)
        )
