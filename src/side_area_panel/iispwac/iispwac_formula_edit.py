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


from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QLabel, QPlainTextEdit

from src.data.data_manager import DATA_MANAGER
from src.pyside_ext.elements.utility.layout_helpers import add_widget
from src.pyside_ext.layout import VBoxLayout
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfig


class _FormulaTextEdit(QPlainTextEdit):
    # A multiline editor with Tab-completion of column names. Tab completes the "unfinished word"
    # before the cursor: the text back to the last backtick when an odd number of backticks precedes
    # the cursor (i.e. a quoted name is open), otherwise back to the last whitespace. If a column
    # name matches (exact, else the first prefix match), it replaces the fragment -- wrapped in
    # backticks when the name needs quoting, or closing the open backtick.
    def __init__(self, parent):
        super().__init__(parent)
        self._column_provider = lambda: []
        self._focus_out_handler = None

    def set_column_provider(self, provider):
        self._column_provider = provider

    def set_focus_out_handler(self, handler):
        self._focus_out_handler = handler

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        if self._focus_out_handler is not None:
            self._focus_out_handler()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Tab:
            if self._autocomplete():
                return
            self.focusNextChild()  # nothing to complete -> keep Tab navigating instead of inserting a tab
            return
        super().keyPressEvent(event)

    def _autocomplete(self) -> bool:
        pos = self.textCursor().position()
        before = self.toPlainText()[:pos]
        open_quote = before.count("`") % 2 == 1
        if open_quote:
            frag_start = before.rfind("`") + 1
        else:
            frag_start = max(before.rfind(" "), before.rfind("\n"), before.rfind("\t")) + 1
        fragment = before[frag_start:]
        if not fragment:
            return False

        match = self._match(fragment, self._column_provider() or [])
        if match is None:
            return False

        if open_quote:
            replacement = match + "`"  # close the quote the user already opened
        elif not match.isidentifier():
            replacement = f"`{match}`"  # a name with spaces/operators must be backtick-quoted
        else:
            replacement = match

        cursor = self.textCursor()
        cursor.setPosition(frag_start)
        cursor.setPosition(pos, QTextCursor.MoveMode.KeepAnchor)
        cursor.insertText(replacement)
        self.setTextCursor(cursor)
        return True

    @staticmethod
    def _match(fragment, names):
        low = fragment.lower()
        for name in names:
            if name.lower() == low:
                return name
        prefix = [name for name in names if name.lower().startswith(low)]
        return prefix[0] if prefix else None


class IISPWACFormulaEdit(ItemInSidePanelWithAutoConfig):
    # A multiline formula field with Tab-completion of column names. The stored value keeps its
    # newlines (for editing larger formulas); the module strips them before evaluating.
    def __init__(self, label_text: str):
        super().__init__()
        self.label_text = label_text
        self._column_names = []

    def post_init(self, name, parent_widget):
        self.name = name
        self.widget, self.layout = add_widget(parent=parent_widget, inner_layout_class=VBoxLayout)
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.layout.setSpacing(5)
        self.label, _ = add_widget(widget=QLabel(self.label_text, self.widget), outer_layout=self.layout)
        self.edit = _FormulaTextEdit(self.widget)
        self.edit.setPlaceholderText("Press Tab to auto-complete column names")
        self.edit.setMinimumHeight(90)
        self.edit.set_column_provider(lambda: self._column_names)
        self.edit.set_focus_out_handler(self.on_recalculate)
        self.layout.addWidget(self.edit)
        self.clear_alert()

    def get_kwargs(self):
        return {self.name: self.edit.toPlainText()}

    def configure(self, **kwargs):
        text = kwargs.get(self.name)
        self.edit.blockSignals(True)
        self.edit.setPlainText(text if text is not None else "")
        self.edit.blockSignals(False)
        data_label = kwargs.get("data_source") or "Auto"
        result_id = kwargs.get("result_id")
        try:
            data = DATA_MANAGER.get_data_from_data_label(data_label=data_label, current_result_id=result_id)
            self._column_names = list(data.column_names())
        except Exception:
            self._column_names = []

    def insert_text(self, text):
        self.edit.insertPlainText(text)
        self.edit.setFocus()

    def set_alert(self):
        set_stylesheet(self.edit, css(border="1px solid red"))

    def clear_alert(self):
        set_stylesheet(self.edit, css(border=Style.General.border_elevated))
