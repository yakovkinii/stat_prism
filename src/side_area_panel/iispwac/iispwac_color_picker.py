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


from PySide6.QtWidgets import QLabel, QPushButton

from src.data.data_manager import DATA_MANAGER
from src.pyside_ext.elements.utility.layout_helpers import add_widget
from src.pyside_ext.layout import HBoxLayout
from src.pyside_ext.markup import css
from src.pyside_ext.overlay_popup import show_color_picker
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfig


class IISPWACColorPicker(ItemInSidePanelWithAutoConfig):
    def __init__(self, label_text: str, default_from_columns: bool = False):
        super().__init__()
        self.label_text = label_text
        # When no colour is stored yet, default to the colour shared by every selected column (if they
        # all share one) -- e.g. a scale built from same-coloured items inherits that colour.
        self.default_from_columns = default_from_columns
        self.color = None

    def post_init(self, name, parent_widget):
        self.name = name
        self.widget, self.layout = add_widget(parent=parent_widget, inner_layout_class=HBoxLayout)
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.layout.setSpacing(5)

        self.label, _ = add_widget(widget=QLabel(self.label_text, self.widget), outer_layout=self.layout)
        self.button, _ = add_widget(widget=QPushButton(self.widget), outer_layout=self.layout)
        self.button.setFixedSize(28, 24)
        self.button.setToolTip("Color tag for the new column")
        self.button.clicked.connect(self._open_picker)
        self._apply_button()

    def _open_picker(self):
        def choose(color):
            # With a column default, "None" must mean "explicitly no colour" (stored as "") so the
            # default does not re-apply on the next configure; otherwise clearing would be undoable.
            if color is None and self.default_from_columns:
                color = ""
            self.color = color
            self._apply_button()
            self.on_recalculate()

        show_color_picker(self.widget, choose)

    def _apply_button(self):
        if isinstance(self.color, str) and self.color:
            set_stylesheet(self.button, css(background=self.color, border="1px solid gray"))
        else:
            set_stylesheet(
                self.button,
                css(background=Style.Color.BackgroundEdit, border=f"1px dashed {Style.Color.BorderElevated}"),
            )

    def get_kwargs(self):
        return {self.name: self.color}

    def configure(self, **kwargs):
        stored = kwargs.get(self.name)
        if stored is None and self.default_from_columns:
            stored = self._common_column_color(kwargs)
        self.color = stored
        self._apply_button()

    def _common_column_color(self, kwargs):
        """The colour shared by every selected column, or None when they are empty, uncoloured, or
        differ. Reads the same config kwargs the framework passes to every element."""
        try:
            data = DATA_MANAGER.get_data_from_data_label(
                data_label=kwargs.get("data_source") or "Auto",
                current_result_id=kwargs["result_id"],
            )
            available = set(data.column_names())
            names = [name for field in (kwargs.get("column_selector") or []) for name in (field or [])]
            colors = [data[name].color for name in names if name in available]
            first = colors[0] if colors else None
            if isinstance(first, str) and first and all(color == first for color in colors):
                return first
            return None
        except Exception:
            return None
