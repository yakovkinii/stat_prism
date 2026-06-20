#  Copyright (c) 2023 StatPrism Team. All rights reserved.

from src.common.constant import ColumnType
from src.pyside_ext.elements.column_selector import Field
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfigHolder
from src.side_area_panel.iispwac.iispwac_checkbox import IISPWACCheckBox
from src.side_area_panel.iispwac.iispwac_column_filter import IISPWACColumnFilter
from src.side_area_panel.iispwac.iispwac_column_selector import IISPWACColumnSelector
from src.side_area_panel.iispwac.iispwac_data_source import IISPWACDataSource
from src.side_area_panel.modules.base.base import BaseModulePanel


class Elements(ItemInSidePanelWithAutoConfigHolder):
    data_source = IISPWACDataSource()

    column_selector = IISPWACColumnSelector(
        fields=[
            Field(
                name="Filter column:",
                column_type=ColumnType.NOMINAL,  # NOMINAL field accepts any column type
                reasonable_number_of_columns=1,
                allow_only_single_column=True,
                minimum_columns=1,
                include_id=True,  # rows may also be filtered by the ID column
            ),
        ],
    )

    column_filter = IISPWACColumnFilter()

    # Backs config.enabled and round-trips through configure()/get_kwargs(); the
    # actual on/off control is the large toggle on the result card, so it is hidden
    # here (see FilterData.setup_ui).
    enabled = IISPWACCheckBox(label_text="Enable filter", default_state=True)


class FilterData(BaseModulePanel):
    def setup_ui(self):
        self.elements_ = Elements().complete_init_of_items(
            parent_widget=self.widget_for_elements,
            parent_layout=self.widget_for_elements_layout,
            handler_on_recalculate=self.recalculate,
            stretch=True,
        )
        self.set_label("Filter")
        # The enable/disable toggle lives on the result card.
        self.elements_.enabled.widget.setVisible(False)
