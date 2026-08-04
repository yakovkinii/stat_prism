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
from src.pyside_ext.elements.column_selector import Field
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfigHolder
from src.side_area_panel.iispwac.iispwac_checkbox import IISPWACCheckBox
from src.side_area_panel.iispwac.iispwac_color_picker import IISPWACColorPicker
from src.side_area_panel.iispwac.iispwac_column_selector import IISPWACColumnSelector
from src.side_area_panel.iispwac.iispwac_combobox import IISPWACComboBox
from src.side_area_panel.iispwac.iispwac_data_source import IISPWACDataSource
from src.side_area_panel.iispwac.iispwac_reference import IISPWACReference
from src.side_area_panel.iispwac.iispwac_spin import IISPWACSpin
from src.side_area_panel.iispwac.iispwac_text_edit import IISPWACLongTextEdit
from src.side_area_panel.modules.base.base import BaseModulePanel

# Dropdown labels for how to handle respondents with missing items.
MISSING_SKIP = "Skip respondent"
MISSING_THRESHOLD = "Allow up to max %"


class Elements(ItemInSidePanelWithAutoConfigHolder):
    data_source = IISPWACDataSource()

    column_selector = IISPWACColumnSelector(
        fields=[
            Field(
                name="Questions:",
                column_type=ColumnType.ORDINAL,
                reasonable_number_of_columns=8,
                allow_only_single_column=False,
                minimum_columns=1,
            ),
            # Reverse-keyed items: flipped first (same reference as Invert Scale), then
            # aggregated together with the normal questions above.
            Field(
                name="Reverse-score first:",
                column_type=ColumnType.ORDINAL,
                reasonable_number_of_columns=8,
                allow_only_single_column=False,
            ),
        ],
    )

    # Reference used to flip the reverse-scored items: auto = (max + min) over their pooled
    # values; tick "Manual" (or edit the value) to override. Only relevant when the
    # "Reverse-score first" field has columns.
    flip_reference = IISPWACReference(label_text="Manual flip reference", field_index=1)
    # Both only matter once reverse-keyed items are chosen; hidden until the second field has columns.
    replace_flipped = IISPWACCheckBox(
        label_text="Replace reverse-scored columns with flipped",
        default_state=True,
        visible_when=lambda kwargs: len(kwargs.get("column_selector") or []) > 1 and bool(kwargs["column_selector"][1]),
    )

    name = IISPWACLongTextEdit(
        label_text="Scale name:",
    )
    method = IISPWACComboBox(
        label_text="Method:",
        items=["Sum", "Mean"],
    )
    scale = IISPWACComboBox(
        label_text="Normalization:",
        items=["None", "Stanine"],
    )
    questions_action = IISPWACComboBox(
        label_text="Questions:",
        items=["Keep", "Auto-rename", "Delete"],
    )
    # How to treat respondents with missing items:
    #  * "Skip respondent" (default): any missing item -> no scale value for that row.
    #  * "Allow up to max %": aggregate over the present items, as long as the share of missing
    #    items does not exceed the threshold below (0% = complete cases only, 100% = always
    #    aggregate over whatever is present).
    missing_values = IISPWACComboBox(
        label_text="Missing values:",
        items=[MISSING_SKIP, MISSING_THRESHOLD],
    )
    missing_threshold = IISPWACSpin(
        label_text="Max missing %:",
        min_value=0,
        max_value=100,
        default_value=0,
    )
    # One color tag shared by the new scale column and the item columns it was built from.
    color = IISPWACColorPicker(label_text="Color:")


class CalculateScale(BaseModulePanel):
    def setup_ui(self):
        self.elements_ = Elements().complete_init_of_items(
            parent_widget=self.widget_for_elements,
            parent_layout=self.widget_for_elements_layout,
            handler_on_recalculate=self.recalculate,
            stretch=True,
        )
        self.set_label("Calculate Scale")
        # "Max missing %" only applies to the threshold mode; hide it for "Skip respondent".
        self.elements_.missing_values.set_handler_current_index_changed(self._sync_missing_enabled)
        self._sync_missing_enabled()

    def _sync_missing_enabled(self):
        visible = self.elements_.missing_values.combo_box.currentText() != MISSING_SKIP
        self.elements_.missing_threshold.widget.setVisible(visible)
