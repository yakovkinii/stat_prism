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
"""Headless test bootstrap.

The calculation functions (``recalculate_*``) are UI-free, but their *import graph*
is not: ``src.pyside_ext.styling`` builds ``QFont`` objects at import time, and the
plot layer imports ``QImage`` / ``QApplication`` and matplotlib. So before any test
module (and therefore any ``src.*`` module) is imported, we must:

  * force Qt onto the offscreen platform (no display needed),
  * force matplotlib onto the Agg backend (no GUI, deterministic raster), and
  * create the single ``QApplication`` instance.

pytest imports ``conftest.py`` before the test modules in its directory, so doing
this at module top level guarantees the app exists before ``styling`` is imported.
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# Snapshot goldens are rendered in one fixed look, so the suite must not depend on the
# developer's local statprism.ini. Force the light UI theme, English, and the default plot
# theme via the STATPRISM_* overrides (honoured in src/common/config.py). These are set
# before any src.* import so the module-level theme/language/plot-theme singletons pick
# them up.
os.environ["STATPRISM_THEME"] = "light"
os.environ["STATPRISM_LANGUAGE"] = "en"
os.environ["STATPRISM_PLOT_THEME"] = "Default"

import matplotlib  # noqa: E402

matplotlib.use("Agg")

from PySide6 import QtWidgets  # noqa: E402

# Keep a module-level reference so the application is not garbage-collected.
_QAPP = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
