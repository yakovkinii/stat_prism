#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from src.common.constant import ColumnType
from src.common.decorators import log_method
from src.common.messages import MessageType
from src.common.progress import run_in_separate_thread
from src.data.data_manager import DATA_MANAGER
from src.pyside_ext.elements.column_selector import Field
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfigHolder
from src.side_area_panel.iispwac.iispwac_checkbox import IISPWACCheckBox
from src.side_area_panel.iispwac.iispwac_column_selector import IISPWACColumnSelector
from src.side_area_panel.iispwac.iispwac_combobox import IISPWACComboBox
from src.side_area_panel.iispwac.iispwac_data_source import IISPWACDataSource
from src.side_area_panel.iispwac.iispwac_text_edit import IISPWACLongTextEdit
from src.side_area_panel.modules.base.base import BaseModulePanel
from src.side_area_panel.modules.common.result.registry import RESULTS


class Elements(ItemInSidePanelWithAutoConfigHolder):
    data_source = IISPWACDataSource()

    column_selector = IISPWACColumnSelector(
        fields=[
            Field(
                name="Column:",
                column_type=ColumnType.ORDINAL,
                reasonable_number_of_columns=1,
                allow_only_single_column=True,
                minimum_columns=1,
            ),
        ],
    )

    rename_to = IISPWACLongTextEdit(
        label_text="Rename to:",
    )
    combo = IISPWACComboBox(
        label_text="Action:",
        items=["Analyze", "Transform", "Encode"],
    )
    check = IISPWACCheckBox(
        label_text="Check",
        default_state=False,
    )


class DpProcessColumn(BaseModulePanel):
    def setup_ui(self):
        self.elements_ = Elements().complete_init_of_items(
            parent_widget=self.widget_for_elements,
            parent_layout=self.widget_for_elements_layout,
            handler_on_recalculate=self.recalculate,
            stretch=True,
        )
        self.set_label("Process Column")
