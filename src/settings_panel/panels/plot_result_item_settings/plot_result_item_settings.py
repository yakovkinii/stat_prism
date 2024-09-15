from typing import TYPE_CHECKING, cast

from src.common.decorators import log_method, log_method_noarg
from src.common.elements.combo_box.combo_box import ComboBox
from src.common.elements.edit.edit import LabeledLineEdit, LabeledMultilineEdit
from src.common.elements.plot_settings.band_plot_settings import BandPlotSettings
from src.common.elements.plot_settings.general_plot_settings import GeneralPlotSettings
from src.common.elements.plot_settings.line_plot_settings import LinePlotSettings
from src.common.elements.plot_settings.scatter_plot_settings import ScatterPlotSettings
from src.common.elements.title.title import Title
from src.common.messages import Message, MessageType
from src.common.result.classes.plot_result import Band, Line, PlotResultElement, Scatter
from src.common.result.registry import RESULTS
from src.settings_panel.panels.base.base import BasePanel

if TYPE_CHECKING:
    pass


class PlotResultItemSettings(BasePanel):
    def setup_ui(self):
        self.elements = {
            "title2": Title(
                label_text="Plot Result Item Settings",
            ),
            "line_edit": LabeledLineEdit("Figure ID:"),
            "title_edit": LabeledMultilineEdit("Title:"),
            "x_axis_title_edit": LabeledLineEdit("X Axis Title:"),
            "y_axis_title_edit": LabeledLineEdit("Y Axis Title:"),
            "general_plot_settings": GeneralPlotSettings(),
            "selector": ComboBox(),
            "scatter_plot_settings": ScatterPlotSettings(),
            "line_plot_settings": LinePlotSettings(),
            "band_plot_settings": BandPlotSettings(),
        }
        self.setup(stretch=True)
        self.elements["line_edit"].edit_widget.editingFinished.connect(self.on_edit_finished)
        self.elements["title_edit"].edit_widget.editingFinished.connect(self.on_edit_finished)
        self.elements["x_axis_title_edit"].edit_widget.editingFinished.connect(self.on_edit_finished)
        self.elements["y_axis_title_edit"].edit_widget.editingFinished.connect(self.on_edit_finished)

    @log_method
    def configure(self, result_id, element_id):
        self.configuring = True
        self.result_id = result_id
        self.element_id = element_id
        self.result_element: PlotResultElement = cast(PlotResultElement, RESULTS[result_id].result_elements[element_id])
        self.elements["line_edit"].edit_widget.setText(self.result_element.plot_id)
        self.elements["title_edit"].edit_widget.setText(self.result_element.plot_title)
        self.elements["x_axis_title_edit"].edit_widget.setText(self.result_element.x_axis_title)
        self.elements["y_axis_title_edit"].edit_widget.setText(self.result_element.y_axis_title)
        self.elements["general_plot_settings"].configure(self.result_element.general_plot_config)

        plot_elements = self.result_element.items
        if plot_elements:
            self.elements["selector"].configure([e.label for e in plot_elements])
            if isinstance(plot_elements[0], Scatter):
                self.elements["scatter_plot_settings"].configure(plot_elements[0].scatter_plot_config)
                self.elements["scatter_plot_settings"].widget.setVisible(True)
                self.elements["line_plot_settings"].widget.setVisible(False)
                self.elements["band_plot_settings"].widget.setVisible(False)
            elif isinstance(plot_elements[0], Line):
                self.elements["line_plot_settings"].configure(plot_elements[0].line_plot_config)
                self.elements["scatter_plot_settings"].widget.setVisible(False)
                self.elements["line_plot_settings"].widget.setVisible(True)
                self.elements["band_plot_settings"].widget.setVisible(False)
            elif isinstance(plot_elements[0], Band):
                self.elements["band_plot_settings"].configure(plot_elements[0].band_plot_config)
                self.elements["scatter_plot_settings"].widget.setVisible(False)
                self.elements["line_plot_settings"].widget.setVisible(False)
                self.elements["band_plot_settings"].widget.setVisible(True)
        else:
            self.elements["scatter_plot_settings"].widget.setVisible(False)
            self.elements["line_plot_settings"].widget.setVisible(False)
            self.elements["band_plot_settings"].widget.setVisible(False)
        self.configuring = False

    @log_method_noarg
    def on_edit_finished(self):
        if self.configuring:
            return
        RESULTS[self.result_id].result_elements[self.element_id].set_plot_id(
            self.elements["line_edit"].edit_widget.text()
        )
        RESULTS[self.result_id].result_elements[self.element_id].set_plot_title(
            self.elements["title_edit"].edit_widget.text()
        )
        RESULTS[self.result_id].result_elements[self.element_id].set_x_axis_title(
            self.elements["x_axis_title_edit"].edit_widget.text()
        )
        RESULTS[self.result_id].result_elements[self.element_id].set_y_axis_title(
            self.elements["y_axis_title_edit"].edit_widget.text()
        )
        self.root_class.results_panel.refresh()

    @log_method
    def handler(self, message: Message):
        if message.message_type == MessageType.STATE_CHANGED:
            if message.caller_id == "general_plot_settings":
                RESULTS[self.result_id].result_elements[self.element_id].general_plot_config = message.payload
                self.elements["general_plot_settings"].configure(message.payload)
                self.root_class.results_panel.refresh()
                return
            if message.caller_id == "scatter_plot_settings":
                RESULTS[self.result_id].result_elements[self.element_id].items[
                    self.elements["selector"].widget.currentIndex()
                ].scatter_plot_config = message.payload
                self.elements["scatter_plot_settings"].configure(message.payload)
                self.root_class.results_panel.refresh()
                return
            if message.caller_id == "line_plot_settings":
                RESULTS[self.result_id].result_elements[self.element_id].items[
                    self.elements["selector"].widget.currentIndex()
                ].line_plot_config = message.payload
                self.elements["line_plot_settings"].configure(message.payload)
                self.root_class.results_panel.refresh()
                return
            if message.caller_id == "band_plot_settings":
                RESULTS[self.result_id].result_elements[self.element_id].items[
                    self.elements["selector"].widget.currentIndex()
                ].band_plot_config = message.payload
                self.elements["band_plot_settings"].configure(message.payload)
                self.root_class.results_panel.refresh()
                return
            if message.caller_id == "selector":
                index = message.payload
                plot_elements = self.result_element.items
                if isinstance(plot_elements[index], Scatter):
                    self.elements["scatter_plot_settings"].configure(plot_elements[index].scatter_plot_config)
                    self.elements["scatter_plot_settings"].widget.setVisible(True)
                    self.elements["line_plot_settings"].widget.setVisible(False)
                    self.elements["band_plot_settings"].widget.setVisible(False)
                elif isinstance(plot_elements[index], Line):
                    self.elements["line_plot_settings"].configure(plot_elements[index].line_plot_config)
                    self.elements["scatter_plot_settings"].widget.setVisible(False)
                    self.elements["line_plot_settings"].widget.setVisible(True)
                    self.elements["band_plot_settings"].widget.setVisible(False)
                elif isinstance(plot_elements[index], Band):
                    self.elements["band_plot_settings"].configure(plot_elements[index].band_plot_config)
                    self.elements["scatter_plot_settings"].widget.setVisible(False)
                    self.elements["line_plot_settings"].widget.setVisible(False)
                    self.elements["band_plot_settings"].widget.setVisible(True)
                return
        super().handler(message)
