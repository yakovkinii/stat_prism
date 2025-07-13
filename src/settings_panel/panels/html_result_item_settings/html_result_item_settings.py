#
#  Copyright (c) 2023 -- 2025 StatPrism Team. All rights reserved.
#
import logging
from typing import TYPE_CHECKING

from src.common.decorators import log_method
from src.common.elements.edit.edit import LabeledLineEdit
from src.common.elements.title.title import Title
from src.settings_panel.panels.base.base import BasePanel

if TYPE_CHECKING:
    pass


class HTMLResultItemSettings(BasePanel):
    def setup_ui(self):
        logging.error("HTMLResultItemSettings is deprecated, use ResultItemSettingsV2 instead.")
        self.elements = {
            "title2": Title(
                label_text="HTML Result Item Settings",
            ),
            "line_edit": LabeledLineEdit(
                label_text="Table ID:",
            ),
            "title_edit": LabeledLineEdit(
                label_text="Title:",
            ),
        }
        self.setup(stretch=True)

    @log_method
    def configure(self, result_id, element_id):
        self.result_id = result_id
        self.element_id = element_id
        # result_element: HTMLResultElement = cast(HTMLResultElement, RESULTS[result_id].result_elements[element_id])

        # self.elements["line_edit"].edit_widget.setText(result_element.table_id)
        # self.elements["title_edit"].edit_widget.setText(result_element.table_caption)
