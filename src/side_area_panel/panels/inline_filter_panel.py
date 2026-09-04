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


import qtawesome as qta

from src.common.constant import RTRIANGLE, ColumnType
from src.data.data_manager import DATA_MANAGER
from src.pyside_ext.elements.column_selector import Field
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfigHolder
from src.side_area_panel.iispwac.iispwac_checkbox import IISPWACCheckBox
from src.side_area_panel.iispwac.iispwac_column_filter import IISPWACColumnFilter
from src.side_area_panel.iispwac.iispwac_column_selector import IISPWACColumnSelector
from src.side_area_panel.iispwac.iispwac_data_source import IISPWACDataSource
from src.side_area_panel.modules.base.base import BaseModulePanel
from src.side_area_panel.modules.common.inline_filter import get_inline_filters
from src.side_area_panel.modules.common.result.registry import RESULTS
from src.side_area_panel.modules.dp_filter.dp_filter_result import FilterDataStudyConfig


class InlineFilterElements(ItemInSidePanelWithAutoConfigHolder):
    # A fresh copy of the Filter module's elements. It must NOT reuse dp_filter's Elements class:
    # iispwac elements are class attributes, so sharing the class would make the two panels fight
    # over the same widget instances.
    data_source = IISPWACDataSource()
    column_selector = IISPWACColumnSelector(
        fields=[
            Field(
                name="Filter column:",
                column_type=ColumnType.NOMINAL,  # NOMINAL accepts any column type
                reasonable_number_of_columns=1,
                allow_only_single_column=True,
                minimum_columns=1,
                include_id=True,
            ),
        ],
    )
    column_filter = IISPWACColumnFilter()
    enabled = IISPWACCheckBox(label_text="Enable filter", default_state=True)


class InlineFilterPanel(BaseModulePanel):
    """Configures one inline filter owned by an analysis. Reached from the analysis card's filter
    block; its Back button returns to the analysis (not Home), like result-element settings."""

    def setup_ui(self):
        self.analysis_id = None
        self.filter_index = None
        self.elements_ = InlineFilterElements().complete_init_of_items(
            parent_widget=self.widget_for_elements,
            parent_layout=self.widget_for_elements_layout,
            handler_on_recalculate=self.recalculate,
            stretch=True,
        )
        self.set_label("Filter")
        # The data source is fixed to the analysis's source; the on/off toggle is unused here.
        self.elements_.data_source.widget.setVisible(False)
        self.elements_.enabled.widget.setVisible(False)
        # Back goes UP to the analysis instead of Home.
        self._cancel_button.setIcon(qta.icon("mdi6.arrow-up-left"))
        self._cancel_button.setToolTip("Back to analysis")
        self._cancel_button.clicked.disconnect()
        self._cancel_button.clicked.connect(self._back_to_analysis)

    def _back_to_analysis(self):
        if self.analysis_id is not None:
            self.root_class.main_area_panel.activate_result(self.analysis_id, None)

    def configure(self, analysis_id, filter_index):
        self.configuring = True
        self.analysis_id = analysis_id
        self.filter_index = filter_index
        analysis = RESULTS[analysis_id]
        cfg = get_inline_filters(analysis)[filter_index]
        cfg.data_source = getattr(analysis.config, "data_source", None) or "Auto"
        # Configure against the analysis's UNFILTERED base data, so the filter sees every value of
        # its column rather than only the ones the other (AND-combined) filters leave.
        DATA_MANAGER._apply_inline = False
        try:
            self.elements_.configure(config=cfg, result_id=analysis_id)
        finally:
            DATA_MANAGER._apply_inline = True
        title = str(analysis.title or "Analysis")
        short = title if len(title) <= 15 else title[:15] + "..."
        self._label.setText(f"{short} {RTRIANGLE} Filter")
        self.configuring = False

    def recalculate(self):
        if self.configuring or self.analysis_id is None:
            return
        analysis = RESULTS[self.analysis_id]
        filters = get_inline_filters(analysis)
        new_config = FilterDataStudyConfig(**self.elements_.get_kwargs())
        new_config.data_source = getattr(analysis.config, "data_source", None) or "Auto"
        filters[self.filter_index] = new_config
        self.elements_.clear_alerts()
        self.root_class.mark_dirty()
        # Recompute the analysis (its data resolution now applies the updated filter) and refresh
        # its card -- without leaving this settings panel.
        panel = self.root_class.settings_panel.panels[analysis.settings_panel_index]
        panel.configure(self.analysis_id)
        panel.recalculate()
        # Re-sync this panel's widgets with the stored config.
        self.configure(self.analysis_id, self.filter_index)
