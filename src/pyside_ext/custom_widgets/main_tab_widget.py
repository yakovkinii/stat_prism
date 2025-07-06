#
#  Copyright (c) 2023 -- 2024 StatPrism Team. All rights reserved.
#

#
#

from PySide6 import QtWidgets
from PySide6.QtWidgets import QTabWidget

from src.common.unique_qss import set_stylesheet
from src.pyside_ext.styling import Style, css

MAIN_TAB_WIDTH = "40px"


def main_tab_widget(parent=None):
    tab_widget = QTabWidget(parent)
    tab_widget.setTabPosition(QtWidgets.QTabWidget.TabPosition.West)
    tab_widget.tabBar().setDocumentMode(True)
    tab_widget.tabBar().setExpanding(True)

    set_stylesheet(
        tab_widget,
        css(
            "QTabWidget#id>QTabBar::tab:selected",
            background=Style.Color.Base,
            font_size=Style.FontSize.regular,
            font_family=Style.FontFamily.SegoeUI,
            font_weight="bold",
            width=MAIN_TAB_WIDTH,
            border="none",
        ),
        css(
            "QTabWidget#id>QTabBar::tab:!selected",
            background=Style.Color.AlternateBase,
            font_size=Style.FontSize.regular,
            font_family=Style.FontFamily.SegoeUI,
            width=MAIN_TAB_WIDTH,
            border="none",
        ),
    )

    return tab_widget
