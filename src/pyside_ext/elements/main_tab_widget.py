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

from PySide6 import QtWidgets
from PySide6.QtWidgets import QTabWidget

from src.pyside_ext.markup import css
from src.pyside_ext.styling import Style
from src.pyside_ext.unique_qss import set_stylesheet


def main_tab_widget(parent=None):
    tab_widget = QTabWidget(parent)
    tab_widget.setTabPosition(QtWidgets.QTabWidget.TabPosition.West)
    tab_widget.tabBar().setDocumentMode(True)
    tab_widget.tabBar().setExpanding(True)

    set_stylesheet(
        tab_widget,
        css(
            "QTabWidget#id>QTabBar::tab:selected",
            background=Style.Color.Background,
            font_size=Style.FontSize.regular,
            font_family=Style.FontFamily.SegoeUI,
            font_weight="bold",
            width=Style.General.main_tab_width_css,
            border="none",
        ),
        css(
            "QTabWidget#id>QTabBar::tab:!selected",
            background=Style.Color.BackgroundElevated,
            font_size=Style.FontSize.regular,
            font_family=Style.FontFamily.SegoeUI,
            width=Style.General.main_tab_width_css,
            border="none",
        ),
    )

    return tab_widget
