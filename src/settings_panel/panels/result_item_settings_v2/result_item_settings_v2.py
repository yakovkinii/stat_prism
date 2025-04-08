#
#  Copyright (c) 2023 -- 2024 StatPrism Team. All rights reserved.
#

import logging
from typing import TYPE_CHECKING, cast

from src.common.decorators import log_method, log_method_noarg
from src.common.elements.edit.edit import LabeledLineEdit, LabeledMultilineEdit
from src.common.elements.group.group_explicit import GroupExplicit
from src.common.elements.plot_settings.band_plot_settings import BandPlotSettings
from src.common.elements.plot_settings.bar_plot_settings import BarPlotSettings
from src.common.elements.plot_settings.box_plot_settings import BoxPlotSettings
from src.common.elements.plot_settings.general_plot_settings import GeneralPlotSettings
from src.common.elements.plot_settings.line_plot_settings import LinePlotSettings
from src.common.elements.plot_settings.scatter_plot_settings import ScatterPlotSettings
from src.common.elements.spacer.spacer_small import SpacerSmall
from src.common.elements.tab.tab import Tab
from src.common.elements.title.title import Title
from src.common.messages import Message, MessageType
from src.common.result.classes.html_result import HTMLTableV2
from src.common.result.classes.plot_result import Band, Bar, Box, Line, PlotResultElement, Scatter
from src.common.result.registry import RESULTS
from src.common.size import SettingsPanelSize
from src.settings_panel.panels.base.base import BasePanel

if TYPE_CHECKING:
    pass


class ResultItemSettingsV2(BasePanel):
    def setup_ui(self):
        self.elements = {
            "title2": Title(
                label_text="Result Item Settings V2",
            ),
            "tab": Tab(),
        }
        self.setup(stretch=False)

    @log_method
    def configure(self, result_id, element_id):
        self.configuring = True
        self.result_id = result_id
        self.element_id = element_id
        self.result_element: HTMLTableV2 = RESULTS[result_id].result_elements[element_id]

        self.elements["tab"].clear_elements_soft()

        self.settings = self.result_element.display_settings
        for name, setting in self.settings.items():
            setting.inject(
                    parent_widget=self.elements["tab"].widget, handler=self.handler, element_id=str(element_id)
                )
            setting.setup()
            self.elements["tab"].add_element(name,setting)

        self.elements["tab"].widget.setFixedWidth(SettingsPanelSize.tab_width)
        self.configuring = False

    @log_method
    def handler(self, message: Message):
        if self.configuring:
            return
        if message.message_type == MessageType.EDITING_FINISHED:
                self.root_class.results_panel.refresh()
                return
        super().handler(message)
