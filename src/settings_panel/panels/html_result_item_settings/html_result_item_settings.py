#
#  Copyright (c) 2024 Ivan I. Yakovkin. All rights reserved.
#

from typing import TYPE_CHECKING, cast

from src.common.decorators import log_method, log_method_noarg
from src.common.elements.edit.edit import LabeledLineEdit, LabeledMultilineEdit
from src.common.elements.title.title import Title
from src.common.result.classes.html_result import HTMLResultElement
from src.common.result.registry import RESULTS
from src.settings_panel.panels.base.base import BasePanel

if TYPE_CHECKING:
    pass


class HTMLResultItemSettings(BasePanel):
    def setup_ui(self):
        self.elements = {
            "title2": Title(
                label_text="HTML Result Item Settings",
            ),
            "line_edit": LabeledLineEdit(
                label_text="Table ID:",
            ),
            "title_edit": LabeledMultilineEdit(
                label_text="Title:",
            ),
        }
        self.setup(stretch=True)
        self.elements["line_edit"].edit_widget.editingFinished.connect(self.on_edit_finished)
        self.elements["title_edit"].edit_widget.editingFinished.connect(self.on_edit_finished)

    @log_method
    def configure(self, result_id, element_id):
        self.result_id = result_id
        self.element_id = element_id
        result_element: HTMLResultElement = cast(HTMLResultElement, RESULTS[result_id].result_elements[element_id])

        self.elements["line_edit"].edit_widget.setText(result_element.table_id)
        self.elements["title_edit"].edit_widget.setText(result_element.table_caption)

    @log_method_noarg
    def on_edit_finished(self):
        RESULTS[self.result_id].result_elements[self.element_id].set_table_id(
            self.elements["line_edit"].edit_widget.text()
        )
        RESULTS[self.result_id].result_elements[self.element_id].set_table_caption(
            self.elements["title_edit"].edit_widget.text()
        )
        self.root_class.results_panel.refresh()
