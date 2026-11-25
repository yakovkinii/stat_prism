#  Copyright (C) 2023-2026  StatPrism Team
#  Balashevych O. K., Petrova N. V., Yakovkin I. I.
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

import os
import sys
from pathlib import Path

APP_DIR_NAME = "StatPrism"


def user_data_dir() -> Path:
    """The per-user, always-writable folder for StatPrism's settings, autosave and log.

    The app's own install directory is frequently read-only -- Windows Program Files, or a macOS
    ``.app`` bundle in /Applications -- so this data must live under a per-user location chosen by
    each platform's convention. (Stdlib only, so it is safe to call before the QApplication exists.)

    * Windows: ``%LOCALAPPDATA%\\StatPrism``                (fallback: ``~/StatPrism``)
    * macOS:   ``~/Library/Application Support/StatPrism``
    * Linux:   ``$XDG_DATA_HOME/StatPrism``                 (fallback: ``~/.local/share/StatPrism``)
    """
    home = os.path.expanduser("~")
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA") or home
        return Path(base) / APP_DIR_NAME
    if sys.platform == "darwin":
        return Path(home) / "Library" / "Application Support" / APP_DIR_NAME
    base = os.environ.get("XDG_DATA_HOME") or os.path.join(home, ".local", "share")
    return Path(base) / APP_DIR_NAME
