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


from PySide6 import QtWidgets
from PySide6.QtGui import QIcon, QPixmap, Qt
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from src.about import version
from src.common.constant import MDASH, NDASH
from src.common.decorators import log_method, log_method_noarg
from src.common.languages import LANGUAGE
from src.common.messages import MessageType
from src.common.theme import THEME
from src.data.data_manager import DATA_MANAGER
from src.pyside_ext.elements.button_large import LargeButton
from src.pyside_ext.elements.spacer import Spacer
from src.savefile.json_store import save_project_json
from src.side_area_panel.blueprint.registry import PanelRegistry
from src.side_area_panel.modules.common.result.registry import RESULTS
from src.side_area_panel.panels.base import BasePanel


class Home(BasePanel):
    def setup_ui(self):
        self.elements = {
            "data_processing": LargeButton(
                label_text="Data Processing",
                icon_path="ri.file-edit-line",
            ),
            "data_analysis": LargeButton(
                label_text="Data Analysis",
                icon_path="ri.bar-chart-line",
            ),
            "spacer": Spacer(),
            "open": LargeButton(
                label_text="Open",
                icon_path="msc.folder-opened",
            ),
            "save": LargeButton(
                label_text="Save",
                icon_path="msc.save",
            ),
            "save_as": LargeButton(
                label_text="Save As",
                icon_path="msc.save-as",
            ),
            "about": LargeButton(
                label_text="About",
                icon_path="ri.questionnaire-line",
            ),
        }

        self.setup(stretch=True, navigation_elements=False)

    @log_method_noarg
    def about_handler(self):
        dlg = AboutDialog(self.widget)
        dlg.exec_()

    @log_method_noarg
    def save_as_handler(self):
        return self.save_handler(save_as=True)

    @log_method
    def save_handler(self, save_as=False) -> bool:
        """Save the project. Returns True if it was written, False if the user backed out
        of the Save As dialog (so callers can keep the unsaved-changes prompt open)."""
        if self.root_class.current_file_path is None or save_as is True:
            file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
                self.widget,
                "Save",
                "",
                "StatPrism project (*.sp);;",
            )
            if not file_path:
                return False
        else:
            file_path = self.root_class.current_file_path

        # Project metadata: StatPrism version + the active theme / language, so the
        # project reopens in the look & language it was saved with. Saved in the JSON+parquet form
        # (see savefile.json_store); the raw dataset and configs are stored and everything else is
        # recomputed on load.
        meta = {
            "version": version,
            "theme": THEME.name(),
            "language": LANGUAGE.language.value,
        }
        save_project_json(file_path, DATA_MANAGER, RESULTS, meta)

        self.root_class.set_current_file_path(file_path)
        self.root_class.clear_dirty()
        return True

    @log_method
    def handler(self, message):
        if message.message_type == MessageType.CLICKED:
            if message.caller_id == "about":
                return self.about_handler()
            elif message.caller_id == "data_processing":
                return self.root_class.action_activate_panel_by_index(
                    PanelRegistry.SELECT_DATA_PROCESSING.settings_stacked_widget_index
                )
            elif message.caller_id == "data_analysis":
                return self.root_class.action_activate_panel_by_index(
                    PanelRegistry.SELECT_DATA_ANALYSIS.settings_stacked_widget_index
                )
            elif message.caller_id == "open":
                return PanelRegistry.HOME_INITIAL.ui_instance.open_handler()
            elif message.caller_id == "save":
                return self.save_handler()
            elif message.caller_id == "save_as":
                return self.save_as_handler()

        return super().handler(message)


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About StatPrism")
        self.setWindowIcon(QIcon(":/mat/resources/icon_small.ico"))
        layout = QVBoxLayout(self)
        banner = QLabel()
        pixmap = QPixmap(":/mat/resources/banner.png")
        if not pixmap.isNull():
            # The banner is ~1675px wide; scale it down to the dialog width so the whole image shows
            # (drawn unscaled it was clipped to a dark left strip, which looked "all black").
            pixmap = pixmap.scaledToWidth(540, Qt.TransformationMode.SmoothTransformation)
            banner.setPixmap(pixmap)
            banner.setAlignment(Qt.AlignCenter)
        layout.addWidget(banner)
        text = QLabel(
            f"""
            <div style="margin-left:32px; text-align:left;">
                <h2 style="text-align:center; margin-bottom:16px;">
                StatPrism {MDASH} version {version} (Developer Edition)
                </h2>
                This version of StatPrism is intended for internal testing only.<br>
                This software is in development and is provided as is, without any guarantees.<br><br>
                Copyright 2023 {NDASH} 2026 StatPrism Team:<br>
                <b>Balashevych A. K.</b> {NDASH} Model Specification;<br>
                <b>Petrova N. V.</b> {NDASH} Testing &amp; QA;<br>
                <b>Yakovkin I. I.</b> {NDASH} Software Development &amp; PM.<br><br>
                <a href="https://www.yakovkinii.com/stat_prism/">www.yakovkinii.com/stat_prism/</a>
                <br><br>
                <span style="font-size:small;">
                StatPrism is free software: you can redistribute it and/or modify it under the
                terms of the <a href="https://www.gnu.org/licenses/gpl-3.0.html">GNU General Public
                License v3.0 or later</a> (see the bundled LICENSE file). It is distributed in the
                hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
                warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
                </span>
            </div>
        """
        )
        text.setTextFormat(Qt.TextFormat.RichText)
        text.setWordWrap(True)  # wrap the long license paragraph instead of clipping it
        text.setOpenExternalLinks(True)
        text.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse)
        text.setAlignment(Qt.AlignLeft)
        layout.addWidget(text)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        btn_layout.addStretch(1)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        self.setMinimumWidth(580)
        self.setMaximumWidth(600)
