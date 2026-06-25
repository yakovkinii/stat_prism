#  Copyright (c) 2023 StatPrism Team. All rights reserved.

from src.common.constant import ColumnType
from src.pyside_ext.elements.column_selector import Field
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfigHolder
from src.side_area_panel.iispwac.iispwac_column_selector import IISPWACColumnSelector
from src.side_area_panel.iispwac.iispwac_data_source import IISPWACDataSource
from src.side_area_panel.iispwac.iispwac_reference import IISPWACReference
from src.side_area_panel.modules.base.base import BaseModulePanel


class Elements(ItemInSidePanelWithAutoConfigHolder):
    data_source = IISPWACDataSource()

    column_selector = IISPWACColumnSelector(
        fields=[
            Field(
                name="Columns:",
                column_type=ColumnType.ORDINAL,
                reasonable_number_of_columns=8,
                allow_only_single_column=False,
                minimum_columns=1,
            ),
        ],
    )

    # All selected columns are inverted with the same reference, auto-inferred as
    # (max + min) over their shared pool of values. Tick "Manual" (or edit the
    # value) to override it, e.g. when the columns lack some possible values.
    reference = IISPWACReference(label_text="Manual")


class InvertScale(BaseModulePanel):
    def setup_ui(self):
        self.elements_ = Elements().complete_init_of_items(
            parent_widget=self.widget_for_elements,
            parent_layout=self.widget_for_elements_layout,
            handler_on_recalculate=self.recalculate,
            stretch=True,
        )
        self.set_label("Invert Scale")
