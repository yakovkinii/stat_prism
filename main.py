#
#  Copyright (c) 2023 -- 2024 StatPrism Team. All rights reserved.
#

import logging

from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QStyleFactory

from src.ui_main import MainWindowClass


def load_all():
    main_win = MainWindowClass()
    # main_win.setStyle(QStyleFactory.create("Fusion"))
    # pal = main_win.style().standardPalette()
    # pal.setColor(QPalette.Window, QColor("#111")) # = "palette(Window)"  # light gray - The general background for widgets
    # pal.setColor(QPalette.WindowText, QColor("#eee")) # = "palette(WindowText)"  # black - Main text drawn on WINDOW surfaces
    # pal.setColor(QPalette.Button, QColor("#444")) # = "palette(Button)"  # light gray - Background for buttons, checkboxes, radio buttons
    # pal.setColor(QPalette.ButtonText, QColor("#eee")) # = "palette(ButtonText)"  # black - Text on buttons (and the “caption” of many controls)
    # pal.setColor(QPalette.Base, QColor("#222")) # = "palette(Base)"  # white - Background for editable fields
    # pal.setColor(QPalette.AlternateBase, QColor("#333")) # = "palette(AlternateBase)"  # lighter gray - Alternate background
    # pal.setColor(QPalette.Text, QColor("#eee")) # = "palette(Text)"  # black - Main text on Base surfaces
    # pal.setColor(QPalette.Highlight, QColor("#eedd88")) # = "palette(Highlight)"  # blue - Background for selected items
    # pal.setColor(QPalette.HighlightedText, QColor("#555")) # = "palette(HighlightedText)"  # white - Text of selected items
    #
    #
    # main_win.setPalette(pal)
    return main_win


logging.debug("main loaded")
