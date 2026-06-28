#  Copyright (c) 2023 StatPrism Team. All rights reserved.
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
# theme via the STATPRISM_* overrides (honoured in src/common/ui_theme.py). These are set
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
