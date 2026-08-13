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


from PySide6 import QtCore
from PySide6.QtWidgets import QLineEdit, QSizePolicy

from src.pyside_ext.elements.utility.primitive_elements import QLabelClickable
from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet
from src.side_area_panel.modules.common.result.registry import RESULTS


class ResultLabel(QLabelClickable):
    def __init__(self, parent, label_text):
        super().__init__(parent)
        self.setText(label_text)
        self.setFont(Style.font_result_label)
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)


class EditableTitle(QLineEdit):
    # A result card's title, renamed in place and stored on the result (RESULTS[id].title), so
    # exports/copy use it and it survives a refresh. The `suffix_fn` part (e.g. " [Data 3]") is
    # shown but dropped while editing and re-appended after. Frameless so it reads as plain text.

    def __init__(self, parent, result_id, suffix_fn=None):
        super().__init__(parent)
        self._result_id = result_id
        self._suffix_fn = suffix_fn or (lambda: "")
        self.setFont(Style.font_study_title)
        self.setFrame(False)
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.NoContextMenu)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        set_stylesheet(self, css(color=Style.Color.TitleBrand, background="transparent", border="none", padding="0"))
        # A QLineEdit does not size to its text; do it so it looks like a label and grows as you type.
        self.textChanged.connect(lambda: self.updateGeometry())
        self.refresh()

    def sizeHint(self):
        base = super().sizeHint()
        return QtCore.QSize(self.fontMetrics().horizontalAdvance(self.text() or "") + 12, base.height())

    def _title(self) -> str:
        # .get: the card can be torn down (result removed) while the field still has focus.
        result = RESULTS.get(self._result_id)
        return result.title if result is not None else self.text()

    def refresh(self):
        if not self.hasFocus():
            self.setText(self._title() + self._suffix_fn())
            self.home(False)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.setText(self._title())  # bare title, without the suffix, while editing
        self.selectAll()

    def focusOutEvent(self, event):
        result = RESULTS.get(self._result_id)
        text = self.text().strip()
        if result is not None and text:
            result.title = text
        super().focusOutEvent(event)
        self.setText(self._title() + self._suffix_fn())
        self.home(False)

    def keyPressEvent(self, event):
        key = event.key()
        if key in (QtCore.Qt.Key.Key_Return, QtCore.Qt.Key.Key_Enter):
            self.clearFocus()  # commit via focusOut
            return
        if key == QtCore.Qt.Key.Key_Escape:
            self.setText(self._title())  # discard the edit, keep the stored title
            self.clearFocus()
            return
        super().keyPressEvent(event)
