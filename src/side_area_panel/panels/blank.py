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


from src.pyside_ext.elements.logo import Logo
from src.side_area_panel.blueprint.registry import PanelRegistry
from src.side_area_panel.panels.base import BasePanel


class Blank(BasePanel):
    def setup_ui(self):
        self.elements = {
            "logo": Logo(),
        }

        self.setup(stretch=False, navigation_elements=False)
        self.elements["logo"].widget.clicked.connect(
            lambda: self.root_class.action_activate_panel_by_index(
                PanelRegistry.SELECT_DATA_ANALYSIS.settings_stacked_widget_index
            )
        )
