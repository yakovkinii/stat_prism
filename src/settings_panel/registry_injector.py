#  Copyright (c) 2023 StatPrism Team. All rights reserved.


from src.modules.common.result.html_result import HTMLTableV2
from src.modules.common.result.plot_result import PlotV2
from src.settings_panel.panels.blank import Blank
from src.settings_panel.panels.column_selector import ColumnSelector
from src.settings_panel.panels.filter import Filter
from src.settings_panel.panels.home import Home
from src.settings_panel.panels.home_initial import HomeInitial
from src.settings_panel.panels.inversion_config import InversionConfig
from src.settings_panel.panels.mapping import Mapping
from src.settings_panel.panels.order import Order
from src.settings_panel.panels.result_item_settings import ResultItemSettingsV2
from src.settings_panel.panels.select_data_processing import SelectDataProcessing
from src.settings_panel.panels.select_study import SelectDataAnalysis
from src.settings_panel.registry import PanelRegistry


def inject_classes_to_panel_registry():
    PanelRegistry.HOME.value.ui_class = Home
    PanelRegistry.HOME_INITIAL.value.ui_class = HomeInitial
    PanelRegistry.SELECT_DATA_ANALYSIS.value.ui_class = SelectDataAnalysis
    PanelRegistry.SELECT_DATA_PROCESSING.value.ui_class = SelectDataProcessing
    PanelRegistry.COLUMN_SELECTOR.value.ui_class = ColumnSelector
    PanelRegistry.FILTER.value.ui_class = Filter
    PanelRegistry.MAPPING.value.ui_class = Mapping
    PanelRegistry.INVERSION_CONFIG.value.ui_class = InversionConfig
    PanelRegistry.BLANK.value.ui_class = Blank
    PanelRegistry.ORDER.value.ui_class = Order
    PanelRegistry.HTML_TABLE_V2_SETTINGS.value.ui_class = ResultItemSettingsV2
    PanelRegistry.HTML_MULTI_TABLE_V2_SETTINGS.value.ui_class = ResultItemSettingsV2
    PanelRegistry.RESULT_ITEM_SETTINGS_V2.value.ui_class = ResultItemSettingsV2
    PanelRegistry.RESULT_ITEM_SETTINGS_V2.value.content_class = [HTMLTableV2, PlotV2]
