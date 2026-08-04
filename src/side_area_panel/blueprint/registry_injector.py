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


from src.side_area_panel.blueprint.registry import PanelRegistry
from src.side_area_panel.modules.common.result.html_result import HTMLTableV2
from src.side_area_panel.modules.common.result.plot_result import PlotV2
from src.side_area_panel.panels.blank import Blank
from src.side_area_panel.panels.column_selector import ColumnSelector
from src.side_area_panel.panels.home import Home
from src.side_area_panel.panels.home_initial import HomeInitial
from src.side_area_panel.panels.inversion_config import InversionConfig
from src.side_area_panel.panels.mapping import Mapping
from src.side_area_panel.panels.order import Order
from src.side_area_panel.panels.result_item_settings import ResultItemSettingsV2
from src.side_area_panel.panels.select_data_processing import SelectDataProcessing
from src.side_area_panel.panels.select_study import SelectDataAnalysis


def inject_classes_to_panel_registry():
    PanelRegistry.HOME.value.ui_class = Home
    PanelRegistry.HOME_INITIAL.value.ui_class = HomeInitial
    PanelRegistry.SELECT_DATA_ANALYSIS.value.ui_class = SelectDataAnalysis
    PanelRegistry.SELECT_DATA_PROCESSING.value.ui_class = SelectDataProcessing
    PanelRegistry.COLUMN_SELECTOR.value.ui_class = ColumnSelector
    PanelRegistry.MAPPING.value.ui_class = Mapping
    PanelRegistry.INVERSION_CONFIG.value.ui_class = InversionConfig
    PanelRegistry.BLANK.value.ui_class = Blank
    PanelRegistry.ORDER.value.ui_class = Order
    PanelRegistry.HTML_TABLE_V2_SETTINGS.value.ui_class = ResultItemSettingsV2
    PanelRegistry.HTML_MULTI_TABLE_V2_SETTINGS.value.ui_class = ResultItemSettingsV2
    PanelRegistry.RESULT_ITEM_SETTINGS_V2.value.ui_class = ResultItemSettingsV2
    PanelRegistry.RESULT_ITEM_SETTINGS_V2.value.content_class = [HTMLTableV2, PlotV2]
