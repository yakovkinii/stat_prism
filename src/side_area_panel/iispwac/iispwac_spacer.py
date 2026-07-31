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

from src.common.decorators import log_method_noarg
from src.side_area_panel.blueprint.element import ItemInSidePanelWithAutoConfig


class IISPWACSpacer(ItemInSidePanelWithAutoConfig):
    def post_init(self, name, parent_widget):
        self.name = name

        self.widget = QWidget(parent_widget)
        self.widget.setFixedHeight(20)

    def get_kwargs(self):
        return {}

    def configure(self, **kwargs):
        pass

    @log_method_noarg
    def set_alert(self):
        pass

    @log_method_noarg
    def clear_alert(self):
        pass
