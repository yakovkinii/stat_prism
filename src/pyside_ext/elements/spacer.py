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

# VALIDATED

from PySide6.QtWidgets import QWidget

from src.pyside_ext.elements.base import BasePanelElement
from src.pyside_ext.styling import Style


class Spacer(BasePanelElement):
    def __init__(self):
        super().__init__()

    def setup(self):
        self.widget = QWidget(self.parent_widget)
        self.widget.setFixedHeight(Style.General.spacer_large.value)
