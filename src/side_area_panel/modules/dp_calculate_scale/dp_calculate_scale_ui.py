#  Copyright (c) 2023 StatPrism Team. All rights reserved.

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
    replace_flipped = IISPWACCheckBox(label_text="Replace reverse-scored columns with flipped", default_state=True)

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
    color = IISPWACColorPicker(label_text="Scale color:")
    questions_color = IISPWACColorPicker(label_text="Questions color:")


class CalculateScale(BaseModulePanel):
    def setup_ui(self):
        self.elements_ = Elements().complete_init_of_items(
            parent_widget=self.widget_for_elements,
            parent_layout=self.widget_for_elements_layout,
            handler_on_recalculate=self.recalculate,
            stretch=True,
        )
        self.set_label("Calculate Scale")
        # "Max missing %" only applies to the threshold mode; grey it out for "Skip respondent".
        self.elements_.missing_values.set_handler_current_index_changed(self._sync_missing_enabled)
        self._sync_missing_enabled()

    def _sync_missing_enabled(self):
        threshold = self.elements_.missing_threshold
        enabled = self.elements_.missing_values.combo_box.currentText() != MISSING_SKIP
        for w in (threshold.spin_box, threshold.minus_button, threshold.plus_button):
            w.setEnabled(enabled)
