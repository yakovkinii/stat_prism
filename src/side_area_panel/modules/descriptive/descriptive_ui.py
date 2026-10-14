#  Copyright (C) 2023-2026  StatPrism Team
#  Balashevych A. K., Petrova N. V., Yakovkin I. I.
#
#  This file is part of StatPrism.
#
#  StatPrism is free software: you can redistribute it and/or modify it under
#  the terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  StatPrism is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with
#  StatPrism.  If not, see <https://www.gnu.org/licenses/>.


from src.common.constant import ColumnType
from src.data.data_manager import DATA_MANAGER
from src.pyside_ext.elements.column_selector import Field
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfigHolder
from src.side_area_panel.iispwac.iispwac_checkbox import IISPWACCheckBox
from src.side_area_panel.iispwac.iispwac_column_selector import IISPWACColumnSelector
from src.side_area_panel.iispwac.iispwac_combobox import IISPWACComboBox
from src.side_area_panel.iispwac.iispwac_data_source import IISPWACDataSource
from src.side_area_panel.iispwac.iispwac_float_protected_spin import IISPWACFloatProtectedSpin
from src.side_area_panel.iispwac.iispwac_float_spin import IISPWACFloatSpin
from src.side_area_panel.iispwac.iispwac_spacer import IISPWACSpacer
from src.side_area_panel.modules.base.base import BaseModulePanel
from src.side_area_panel.modules.common.prose import PROSE_LABEL, PROSE_LEVELS
from src.side_area_panel.modules.common.result.plot_result import PIE_COLORMAPS

NORMALITY_TESTS = ["Shapiro-Wilk", "Kolmogorov-Smirnov", "Anderson-Darling"]


def _selected_variable_types(kwargs):
    """Column types among the currently selected analysis variables (the first column-selector
    field). Empty while nothing is selected."""
    selection = kwargs.get("column_selector")
    if not selection or not selection[0]:
        return set()
    data_label = kwargs.get("data_source") or "Auto"
    columns = DATA_MANAGER.get_data_from_data_label(
        data_label=data_label,
        current_result_id=kwargs.get("result_id"),
    ).get_all_columns_as_column_types()
    by_name = {column.column_name: column.column_type for column in columns}
    return {by_name[name] for name in selection[0] if name in by_name}


# Each returns True while nothing is selected yet, so the full set of options shows until the
# selection narrows things down. Quantitative = numeric or ordinal (ordinal is code-mapped);
# categorical = nominal; "has categories" (pie) = anything with discrete labels.
def _has_quantitative(kwargs):
    types = _selected_variable_types(kwargs)
    return not types or bool(types & {ColumnType.NUMERIC, ColumnType.ORDINAL})


def _has_numeric(kwargs):
    types = _selected_variable_types(kwargs)
    return not types or ColumnType.NUMERIC in types


def _has_categorical(kwargs):
    types = _selected_variable_types(kwargs)
    return not types or ColumnType.NOMINAL in types


def _has_categories(kwargs):
    types = _selected_variable_types(kwargs)
    return not types or bool(types & {ColumnType.ORDINAL, ColumnType.NOMINAL})


def _has_plottable_categories(kwargs):
    return _has_categories(kwargs) or (bool(kwargs.get("frequency_table_numeric")) and _has_numeric(kwargs))


def _has_ordinal(kwargs):
    types = _selected_variable_types(kwargs)
    return not types or ColumnType.ORDINAL in types


class Elements(ItemInSidePanelWithAutoConfigHolder):
    data_source = IISPWACDataSource()
    column_selector = IISPWACColumnSelector(
        fields=[
            Field(
                name="Variable(s):",
                column_type=ColumnType.NOMINAL,
                reasonable_number_of_columns=8,
                minimum_columns=1,
            ),
            Field(
                name="Grouping Column (optional):",
                column_type=ColumnType.NOMINAL,
                reasonable_number_of_columns=1,
                allow_only_single_column=True,
            ),
        ],
    )
    spacer = IISPWACSpacer()
    # Options irrelevant to the selected column types are hidden: quantitative-only items
    # (numeric summary / normality / distribution / box / Q-Q) disappear when only nominal
    # variables are chosen, and the categorical-only items when only quantitative ones are.
    # --- Tables ---
    extended_stats = IISPWACCheckBox(
        label_text="Extended numeric stats", default_state=False, visible_when=_has_quantitative
    )
    frequency_table = IISPWACCheckBox(
        label_text="Categorical frequency table", default_state=True, visible_when=_has_categorical
    )
    frequency_table_ordinal = IISPWACCheckBox(
        label_text="Ordinal frequency table", default_state=False, visible_when=_has_ordinal
    )
    frequency_table_numeric = IISPWACCheckBox(
        label_text="Numeric frequency table", default_state=False, visible_when=_has_numeric
    )
    show_normality = IISPWACCheckBox(label_text="Normality test", default_state=True, visible_when=_has_quantitative)
    normality_test = IISPWACComboBox(
        label_text="Normality test:", items=NORMALITY_TESTS, visible_when=_has_quantitative
    )
    verbal_indicators = IISPWACCheckBox(label_text="Verbal indicators in tables", default_state=False)
    interpretation = IISPWACComboBox(label_text=PROSE_LABEL, items=PROSE_LEVELS)
    number_columns = IISPWACCheckBox(label_text="Number variables in tables", default_state=False)
    # --- Plots (each opt-in) ---
    show_distribution = IISPWACCheckBox(
        label_text="Distribution plots", default_state=False, visible_when=_has_quantitative
    )
    show_box = IISPWACCheckBox(label_text="Box plots", default_state=False, visible_when=_has_quantitative)
    mark_outliers = IISPWACCheckBox(
        label_text="Label outliers on box plots", default_state=False, visible_when=_has_quantitative
    )
    show_frequency_bars = IISPWACCheckBox(
        label_text="Frequency bar charts", default_state=False, visible_when=_has_plottable_categories
    )
    show_pie = IISPWACCheckBox(label_text="Pie charts", default_state=False, visible_when=_has_plottable_categories)
    pie_colormap = IISPWACComboBox(
        label_text="Pie colors:",
        items=PIE_COLORMAPS,
        visible_when=lambda kwargs: bool(kwargs.get("show_pie")) and _has_plottable_categories(kwargs),
    )
    pie_show_percent = IISPWACCheckBox(
        label_text="Pie legend: %",
        default_state=True,
        visible_when=lambda kwargs: bool(kwargs.get("show_pie")) and _has_plottable_categories(kwargs),
    )
    pie_show_counts = IISPWACCheckBox(
        label_text="Pie legend: counts",
        default_state=False,
        visible_when=lambda kwargs: bool(kwargs.get("show_pie")) and _has_plottable_categories(kwargs),
    )
    pie_donut_hole = IISPWACFloatSpin(
        label_text="Pie donut hole:",
        min_value=0.0,
        max_value=0.8,
        default_value=0.42,
        decimals=1,
        step=0.1,
        visible_when=lambda kwargs: bool(kwargs.get("show_pie")) and _has_plottable_categories(kwargs),
    )
    pie_gap = IISPWACFloatSpin(
        label_text="Pie slice gap:",
        min_value=0.0,
        max_value=0.16,
        default_value=0.08,
        decimals=2,
        step=0.01,
        visible_when=lambda kwargs: bool(kwargs.get("show_pie")) and _has_plottable_categories(kwargs),
    )
    pie_outline_width = IISPWACFloatSpin(
        label_text="Pie outline width:",
        min_value=0.0,
        max_value=5.0,
        default_value=1.5,
        decimals=1,
        step=0.5,
        visible_when=lambda kwargs: bool(kwargs.get("show_pie")) and _has_plottable_categories(kwargs),
    )
    pie_shadow = IISPWACCheckBox(
        label_text="Pie shadow",
        default_state=True,
        visible_when=lambda kwargs: bool(kwargs.get("show_pie")) and _has_plottable_categories(kwargs),
    )
    pie_shadow_size = IISPWACFloatSpin(
        label_text="Pie shadow size:",
        min_value=0.005,
        max_value=0.08,
        default_value=0.01,
        decimals=3,
        step=0.005,
        visible_when=lambda kwargs: bool(kwargs.get("show_pie"))
        and bool(kwargs.get("pie_shadow"))
        and _has_plottable_categories(kwargs),
    )
    pie_hatch = IISPWACCheckBox(
        label_text="Pie hatch",
        default_state=True,
        visible_when=lambda kwargs: bool(kwargs.get("show_pie")) and _has_plottable_categories(kwargs),
    )
    pie_legend_spacing = IISPWACFloatSpin(
        label_text="Pie legend spacing:",
        min_value=0.1,
        max_value=2.0,
        default_value=0.75,
        decimals=1,
        step=0.1,
        visible_when=lambda kwargs: bool(kwargs.get("show_pie")) and _has_plottable_categories(kwargs),
    )
    show_qq = IISPWACCheckBox(label_text="Q-Q plots", default_state=False, visible_when=_has_quantitative)
    # --- Distribution-plot controls ---
    show_kde = IISPWACCheckBox(label_text="Show KDE curve", default_state=True, visible_when=_has_quantitative)
    # Bin / KDE controls only apply while distribution plots (and KDE) are shown, and only for
    # quantitative variables.
    # Bin width has no clean default (auto = data-dependent), so it is off by default and the manual
    # spin is greyed until ticked. Bin reference has a clean default (0) and KDE smoothing a clean
    # default (1), so those are plain always-on spins.
    bin_width = IISPWACFloatProtectedSpin(
        label_text="Manual bin width",
        min_value=0.0001,
        max_value=1000000.0,
        default_value=1.0,
        decimals=2,
        step=1.0,
        visible_when=lambda kwargs: bool(kwargs.get("show_distribution")) and _has_quantitative(kwargs),
    )
    bin_reference = IISPWACFloatSpin(
        label_text="Bin reference:",
        min_value=-1000000.0,
        max_value=1000000.0,
        default_value=0.0,
        decimals=2,
        step=1.0,
        visible_when=lambda kwargs: bool(kwargs.get("show_distribution")) and _has_quantitative(kwargs),
    )
    kde_smoothing = IISPWACFloatSpin(
        label_text="KDE smoothing:",
        min_value=0.1,
        max_value=10.0,
        default_value=1.0,
        decimals=1,
        step=0.1,
        visible_when=lambda kwargs: bool(kwargs.get("show_distribution"))
        and bool(kwargs.get("show_kde"))
        and _has_quantitative(kwargs),
    )


class Descriptive(BaseModulePanel):
    def setup_ui(self):
        self.init_elements(Elements)
        self.set_label("Descriptive Statistics")
