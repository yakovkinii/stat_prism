# #
# #  Copyright (c) 2023 -- 2024 StatPrism Team. All rights reserved.
# #
#
# import logging
# from typing import TYPE_CHECKING, cast
#
# from src.common.decorators import log_method, log_method_noarg
# from src.common.elements.edit.edit import LabeledLineEdit, LabeledMultilineEdit
# from src.common.elements.group.group_explicit import GroupExplicit
# from src.common.elements.plot_settings.band_plot_settings import BandPlotSettings
# from src.common.elements.plot_settings.bar_plot_settings import BarPlotSettings
# from src.common.elements.plot_settings.box_plot_settings import BoxPlotSettings
# from src.common.elements.plot_settings.general_plot_settings import GeneralPlotSettings
# from src.common.elements.plot_settings.line_plot_settings import LinePlotSettings
# from src.common.elements.plot_settings.scatter_plot_settings import ScatterPlotSettings
# from src.common.elements.spacer.spacer_small import SpacerSmall
# from src.common.elements.title.title import Title
# from src.common.messages import Message, MessageType
# from src.common.result.classes.plot_result import Band, Bar, Box, Line, PlotResultElement, Scatter
# from src.common.result.registry import RESULTS
# from src.settings_panel.panels.base.base import BasePanel
#
# if TYPE_CHECKING:
#     pass
#
#
# class PlotResultItemSettings(BasePanel):
#     def setup_ui(self):
#         self.elements = {
#             "title2": Title(
#                 label_text="Plot Result Item Settings",
#             ),
#             "line_edit": LabeledLineEdit("Figure ID:"),
#             "title_edit": LabeledMultilineEdit("Title:"),
#             "x_axis_title_edit": LabeledLineEdit("X Axis Title:"),
#             "y_axis_title_edit": LabeledLineEdit("Y Axis Title:"),
#             "spacer": SpacerSmall(),
#             "general_plot_settings": GeneralPlotSettings(),
#             "spacer2": SpacerSmall(),
#             "group": GroupExplicit(),
#         }
#         self.setup(stretch=True)
#         self.elements["line_edit"].edit_widget.editingFinished.connect(self.on_edit_finished)
#         self.elements["title_edit"].edit_widget.editingFinished.connect(self.on_edit_finished)
#         self.elements["x_axis_title_edit"].edit_widget.editingFinished.connect(self.on_edit_finished)
#         self.elements["y_axis_title_edit"].edit_widget.editingFinished.connect(self.on_edit_finished)
#
#     @log_method
#     def configure(self, result_id, element_id):
#         self.configuring = True
#         self.result_id = result_id
#         self.element_id = element_id
#         self.result_element: PlotResultElement = cast(PlotResultElement,
#         RESULTS[result_id].result_elements[element_id])
#
#         self.elements["line_edit"].edit_widget.setText(self.result_element.plot_id)
#         self.elements["title_edit"].edit_widget.setText(self.result_element.plot_title)
#         self.elements["x_axis_title_edit"].edit_widget.setText(self.result_element.x_axis_title)
#         self.elements["y_axis_title_edit"].edit_widget.setText(self.result_element.y_axis_title)
#         self.elements["general_plot_settings"].configure(self.result_element.general_plot_config)
#
#         self.elements["x_axis_title_edit"].edit_widget.setCursorPosition(0)
#         self.elements["y_axis_title_edit"].edit_widget.setCursorPosition(0)
#
#         plot_elements = self.result_element.items
#         self.elements["group"].clear_elements()
#         for plot_element_id, plot_element in enumerate(plot_elements):
#             if isinstance(plot_element, Scatter):
#                 plot_settings = ScatterPlotSettings(plot_element.label)
#             elif isinstance(plot_element, Line):
#                 plot_settings = LinePlotSettings(plot_element.label)
#             elif isinstance(plot_element, Band):
#                 plot_settings = BandPlotSettings(plot_element.label)
#             elif isinstance(plot_element, Bar):
#                 plot_settings = BarPlotSettings(plot_element.label)
#             elif isinstance(plot_element, Box):
#                 plot_settings = BoxPlotSettings(plot_element.label)
#             else:
#                 self.configuring = False
#                 return
#                 # raise ValueError(f"Unknown plot element type: {type(plot_element)}")
#
#             plot_settings.inject(
#                 parent_widget=self.elements["group"].widget, handler=self.handler, element_id=str(plot_element_id)
#             )
#             plot_settings.setup()
#             plot_settings.configure(plot_element.config)
#             self.elements["group"].add_element(plot_settings)
#
#         self.configuring = False
#
#     @log_method_noarg
#     def on_edit_finished(self):
#         if self.configuring:
#             return
#         result_element: PlotResultElement = cast(
#             PlotResultElement, RESULTS[self.result_id].result_elements[self.element_id]
#         )
#         result_element.set_plot_id(self.elements["line_edit"].edit_widget.text())
#         result_element.set_plot_title(self.elements["title_edit"].edit_widget.text())
#         result_element.set_x_axis_title(self.elements["x_axis_title_edit"].edit_widget.text())
#         result_element.set_y_axis_title(self.elements["y_axis_title_edit"].edit_widget.text())
#         self.root_class.results_panel.refresh()
#
#     @log_method
#     def handler(self, message: Message):
#         if self.configuring:
#             return
#         if message.message_type == MessageType.STATE_CHANGED:
#             if message.caller_id == "general_plot_settings":
#                 RESULTS[self.result_id].result_elements[self.element_id].general_plot_config = message.payload
#                 self.elements["general_plot_settings"].configure(message.payload)
#                 self.root_class.results_panel.refresh()
#                 return
#
#             # id should be the item #
#             try:
#                 item_id = int(message.caller_id)
#                 RESULTS[self.result_id].result_elements[self.element_id].items[item_id].config = message.payload
#                 self.elements["group"].get_elements(item_id).configure(message.payload)
#                 self.root_class.results_panel.refresh()
#                 return
#             except ValueError:
#                 logging.error(f"Invalid plot item id: {message.caller_id}")
#                 super().handler(message)
#
#         super().handler(message)
