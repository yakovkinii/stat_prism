#  Copyright (c) 2023 StatPrism Team. All rights reserved.

from src.common.constant import ColumnType
from src.pyside_ext.elements.column_selector import Field
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfigHolder
from src.side_area_panel.iispwac.iispwac_checkbox import IISPWACCheckBox
from src.side_area_panel.iispwac.iispwac_color_picker import IISPWACColorPicker
from src.side_area_panel.iispwac.iispwac_column_selector import IISPWACColumnSelector
from src.side_area_panel.iispwac.iispwac_combobox import IISPWACComboBox
from src.side_area_panel.iispwac.iispwac_data_source import IISPWACDataSource
from src.side_area_panel.iispwac.iispwac_text_edit import IISPWACLongTextEdit
from src.side_area_panel.modules.base.base import BaseModulePanel


class Elements(ItemInSidePanelWithAutoConfigHolder):
    data_source = IISPWACDataSource()

    column_selector = IISPWACColumnSelector(
        fields=[
            Field(
                name="Questions:",
                column_type=ColumnType.ORDINAL,
                reasonable_number_of_columns=10,
                allow_only_single_column=False,
                minimum_columns=1,
            ),
        ],
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
    # Off (default): any missing item makes the scale value missing for that row.
    # On: missing items are skipped and the scale is aggregated over the present ones.
    exclude_missing = IISPWACCheckBox(
        label_text="Aggregate despite missing values",
        default_state=False,
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
