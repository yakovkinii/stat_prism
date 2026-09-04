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


from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QAbstractItemView, QLabel, QListWidget, QListWidgetItem, QSizePolicy

from src.common.constant import ColumnType, column_text_color
from src.data.data_manager import DATA_MANAGER
from src.pyside_ext.elements.utility.layout_helpers import add_widget
from src.pyside_ext.layout import VBoxLayout
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfig


class IISPWACColumnReorderList(ItemInSidePanelWithAutoConfig):
    # A single drag-to-reorder list of ALL (non-ID) columns -- no column selector. Rows are kept
    # compact so a whole dataset fits with little scrolling. The stored value is the column order.
    def __init__(self, label_text: str = "Drag columns to set their order:"):
        super().__init__()
        self.label_text = label_text
        self._suppress = False

    def post_init(self, name, parent_widget):
        self.name = name
        self.widget, self.layout = add_widget(parent=parent_widget, inner_layout_class=VBoxLayout)
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.layout.setSpacing(5)
        # The element (and the list inside it) expand vertically so the list fills the panel height.
        self.widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.label, _ = add_widget(widget=QLabel(self.label_text, self.widget), outer_layout=self.layout)
        self.list_widget, _ = add_widget(widget=QListWidget(self.widget), outer_layout=self.layout)
        self.list_widget.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.list_widget.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.list_widget.setUniformItemSizes(True)
        self.list_widget.setMinimumHeight(200)
        self.list_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # Compact rows so more columns fit without scrolling.
        set_stylesheet(
            self.list_widget,
            css(border=Style.General.border_elevated),
            css(selector="QListWidget::item", padding="1px 4px"),
        )
        # Recompute after a drag-drop reorder. Done via dropEvent (deferred a tick so the model has
        # settled) because a QListWidget internal move does not reliably emit rowsMoved.
        self.list_widget.dropEvent = self._drop_event

    def _drop_event(self, event):
        QListWidget.dropEvent(self.list_widget, event)
        if not self._suppress:
            QTimer.singleShot(0, self._on_reorder)

    def configure(self, **kwargs):
        data_label = kwargs.get("data_source") or "Auto"
        result_id = kwargs.get("result_id")
        saved = kwargs.get(self.name) or []
        color_by = {}
        try:
            data = DATA_MANAGER.get_data_from_data_label(data_label=data_label, current_result_id=result_id)
            columns = [c for c in data.columns if c.column_type != ColumnType.ID]
            names = [c.column_name for c in columns]
            color_by = {c.column_name: c.color for c in columns}
        except Exception:
            names = []
        # Saved order first (existing columns only), then any columns new since it was saved.
        saved_set = set(saved)
        ordered = [n for n in saved if n in names] + [n for n in names if n not in saved_set]
        # Rebuilding resets the scroll to the top; keep the user where they were (a reorder triggers
        # a recompute, which reconfigures this list right after a drop).
        scroll_value = self.list_widget.verticalScrollBar().value()
        self._suppress = True
        self.list_widget.clear()
        for column_name in ordered:
            item = QListWidgetItem(column_name)
            color = color_by.get(column_name)
            # Show the column's color tag, with black/white text chosen for legibility on it
            # (matching the data viewer / column selector).
            if isinstance(color, str) and color:
                item.setBackground(QColor(color))
                item.setForeground(QColor(column_text_color(color)))
            self.list_widget.addItem(item)
        self._suppress = False
        self.list_widget.verticalScrollBar().setValue(scroll_value)

    def get_kwargs(self):
        return {self.name: [self.list_widget.item(i).text() for i in range(self.list_widget.count())]}

    def _on_reorder(self, *args):
        if not self._suppress:
            self.on_recalculate()

    def set_alert(self):
        pass

    def clear_alert(self):
        pass
