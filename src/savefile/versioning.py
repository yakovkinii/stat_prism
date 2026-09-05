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

"""Project-file (.sp) versioning.

Versioning is ``a.b.c``: bumping ``a`` or ``b`` is a *breaking* change to the save format, while
``c`` is compatible. So a file is openable by this build when its ``(a, b)`` is not newer than the
build's ``(a, b)``:

* file ``(a, b)`` > app ``(a, b)``  -> refuse (saved by a newer, incompatible version);
* file ``(a, b)`` < app ``(a, b)``  -> migrate the JSON project dict up one ``b`` at a time;
* equal                              -> load directly.

Migrations therefore have one link per ``b`` bump. They operate on the plain JSON project dict (not
pickles), so they stay small and are quarantined here rather than spread through the app.
"""

import logging

from src.about import version as APP_VERSION


class IncompatibleProjectError(Exception):
    """A project file cannot be opened by this version of StatPrism (it was saved by a newer one)."""


def parse_version(text):
    """``"1.2.8"`` -> ``(1, 2, 8)``, tolerant of missing/short/garbage input."""
    nums = []
    for part in str(text or "0.0.0").split(".")[:3]:
        try:
            nums.append(int(part))
        except ValueError:
            nums.append(0)
    while len(nums) < 3:
        nums.append(0)
    return tuple(nums)


APP_A, APP_B, APP_C = parse_version(APP_VERSION)


def check_openable(meta):
    """Raise :class:`IncompatibleProjectError` if the project was saved by a newer breaking version
    (a newer ``a`` or ``b``); otherwise return the parsed ``(a, b, c)`` of the file."""
    file_version = parse_version((meta or {}).get("version"))
    if file_version[:2] > (APP_A, APP_B):
        fa, fb, fc = file_version
        raise IncompatibleProjectError(
            f"This project was saved with StatPrism {fa}.{fb}.{fc}, which is newer than this version "
            f"({APP_VERSION}). Please update StatPrism to open it."
        )
    return file_version


def _migrate_reorder_to_arrange(project_dict):
    """1.3.0 removed the deprecated Reorder Columns module. Convert any such saved step into an
    Arrange Columns step so the project still loads. The old block-move can't be mapped to a full
    column order exactly, so it becomes a pass-through (empty order) -- the study stays in the chain,
    in natural order, for the user to redo if needed."""
    for entry in project_dict.get("results", []):
        if entry.get("module") == "REORDER_COLUMNS":
            entry["module"] = "ARRANGE_COLUMNS"
            old_config = entry.get("config") or {}
            entry["config"] = {"data_source": old_config.get("data_source") or "Auto", "order": []}
    return project_dict


# Ordered converters on the JSON project dict, one per version that changed the save shape -- patch
# (``c``) bumps included, not only breaking (``b``) ones. Each is ``(version_it_upgrades_TO, fn)``,
# a pure ``project_dict -> project_dict``. On load, every converter whose target is above the file's
# version and not above this build's is applied in version order.
_MIGRATIONS = [
    ("1.3.0", _migrate_reorder_to_arrange),
]


def migrate_project(project_dict, file_version):
    """Bring a loaded JSON project dict up to this build's version by applying every registered
    converter whose target version is above the file's and at most this build's, in order."""
    file_v = parse_version(file_version)
    app_v = (APP_A, APP_B, APP_C)
    for target, migrate in sorted(_MIGRATIONS, key=lambda entry: parse_version(entry[0])):
        target_v = parse_version(target)
        if file_v < target_v <= app_v:
            logging.info("Migrating project %s -> %s", file_version, target)
            project_dict = migrate(project_dict)
            file_v = target_v
    return project_dict
