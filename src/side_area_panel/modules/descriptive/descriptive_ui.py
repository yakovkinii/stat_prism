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
from src.side_area_panel.iispwac.iispwac_spacer import IISPWACSpacer
from src.side_area_panel.iispwac.iispwac_text_edit import IISPWACLongTextEdit
from src.side_area_panel.modules.base.base import BaseModulePanel
from src.side_area_panel.modules.common.prose import PROSE_LABEL, PROSE_LEVELS

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


def _has_categorical(kwargs):
    types = _selected_variable_types(kwargs)
    return not types or ColumnType.NOMINAL in types


def _has_categories(kwargs):
    types = _selected_variable_types(kwargs)
    return not types or bool(types & {ColumnType.ORDINAL, ColumnType.NOMINAL})


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
        label_text="Frequency bar charts", default_state=False, visible_when=_has_categorical
    )
    show_pie = IISPWACCheckBox(label_text="Pie charts", default_state=False, visible_when=_has_categories)
    show_qq = IISPWACCheckBox(label_text="Q-Q plots", default_state=False, visible_when=_has_quantitative)
    # --- Distribution-plot controls ---
    show_kde = IISPWACCheckBox(label_text="Show KDE curve", default_state=True, visible_when=_has_quantitative)
    # Bin / KDE controls only apply while distribution plots (and KDE) are shown, and only for
    # quantitative variables.
    bin_width = IISPWACLongTextEdit(
        label_text="Bin width (blank: auto):",
        visible_when=lambda kwargs: bool(kwargs.get("show_distribution")) and _has_quantitative(kwargs),
    )
    bin_reference = IISPWACLongTextEdit(
        label_text="Bin reference (blank: auto):",
        visible_when=lambda kwargs: bool(kwargs.get("show_distribution")) and _has_quantitative(kwargs),
    )
    kde_smoothing = IISPWACLongTextEdit(
        label_text="KDE smoothing (blank: auto; <1: sharper; >1: smoother):",
        visible_when=lambda kwargs: bool(kwargs.get("show_distribution"))
        and bool(kwargs.get("show_kde"))
        and _has_quantitative(kwargs),
    )


class Descriptive(BaseModulePanel):
    def setup_ui(self):
        self.init_elements(Elements)
        self.set_label("Descriptive Statistics")
