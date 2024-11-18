#
#  Copyright (c) 2024 Ivan I. Yakovkin. All rights reserved.
#

from src.settings_panel.panels.blank.blank import Blank
from src.settings_panel.panels.column.column import Column
from src.settings_panel.panels.column_selector.column_selector import ColumnSelector
from src.settings_panel.panels.columns.columns import Columns
from src.settings_panel.panels.filter.filter import Filter
from src.settings_panel.panels.home.home import Home
from src.settings_panel.panels.html_result_item_settings.html_result_item_settings import HTMLResultItemSettings
from src.settings_panel.panels.invert.invert import Inverse
from src.settings_panel.panels.order.order import Order
from src.settings_panel.panels.plot_result_item_settings.plot_result_item_settings import PlotResultItemSettings
from src.settings_panel.panels.registry import PanelRegistry
from src.settings_panel.panels.select_study.select_study import SelectStudy


def inject_classes_to_panel_registry():
    PanelRegistry.HOME.value.ui_class = Home
    PanelRegistry.SELECT_STUDY.value.ui_class = SelectStudy
    PanelRegistry.COLUMN_SELECTOR.value.ui_class = ColumnSelector
    PanelRegistry.FILTER.value.ui_class = Filter
    PanelRegistry.COLUMNS.value.ui_class = Columns
    PanelRegistry.COLUMN.value.ui_class = Column
    PanelRegistry.INVERSE.value.ui_class = Inverse
    PanelRegistry.HTML_RESULT_ITEM_SETTINGS.value.ui_class = HTMLResultItemSettings
    PanelRegistry.PLOT_RESULT_ITEM_SETTINGS.value.ui_class = PlotResultItemSettings
    PanelRegistry.BLANK.value.ui_class = Blank
    PanelRegistry.ORDER.value.ui_class = Order
