#
#  Copyright (c) 2024 Ivan I. Yakovkin. All rights reserved.
#

import logging

from src.ui_main import MainWindowClass


def load_all():
    main_win = MainWindowClass()
    return main_win


logging.debug("main loaded")
