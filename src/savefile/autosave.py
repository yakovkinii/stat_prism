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


import logging
import os
import shutil
from pathlib import Path

from PySide6.QtCore import QTimer

from src.about import version
from src.common.config import read_autosave_enabled
from src.common.languages import LANGUAGE
from src.common.theme import THEME
from src.data.data_manager import DATA_MANAGER
from src.savefile.json_store import write_project_bundle
from src.side_area_panel.modules.common.result.registry import RESULTS


def autosave_dir() -> Path:
    # A single rolling snapshot of the current session, in the per-user app-data folder (the same
    # place the launcher writes its log). The user never sees it; it exists only so a crash can be
    # recovered. One slot, not per-project -- it is always "the last session".
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    return Path(base) / "StatPrism" / "autosave"


# Owns the crash-recovery autosave: a compact JSON snapshot (chain + configs, plus the raw dataset
# written lazily) kept in autosave_dir(). It is refreshed on a 5-minute idle backstop and brought
# forward to ~30s after any change, so a burst of edits (e.g. tuning a data-processing step) is
# coalesced into one save instead of saving on every change. A clean exit clears the snapshot, so a
# snapshot present at the next start means the previous session crashed.
class AutoSaveManager:
    PERIODIC_MS = 5 * 60 * 1000
    EXPEDITE_MS = 30 * 1000

    def __init__(self, root_class):
        self.root_class = root_class
        # The raw dataset only changes on import / project open; track that so the heavy parquet is
        # rewritten only then, not on every tick.
        self._raw_dirty = True

        self._periodic = QTimer(root_class)
        self._periodic.setInterval(self.PERIODIC_MS)
        self._periodic.timeout.connect(self.perform_autosave)
        self._expedite = QTimer(root_class)
        self._expedite.setSingleShot(True)
        self._expedite.timeout.connect(self.perform_autosave)

        if read_autosave_enabled():
            self._periodic.start()

    def set_enabled(self, enabled: bool):
        if enabled:
            self._periodic.start()
        else:
            self._periodic.stop()
            self._expedite.stop()

    def notify_changed(self):
        # A change happened: bring the next save forward to EXPEDITE_MS unless one is already
        # pending (so a burst of edits coalesces into a single save). The periodic timer remains the
        # idle backstop. No-op when autosave is disabled.
        if not self._periodic.isActive():
            return
        if not self._expedite.isActive():
            self._expedite.start(self.EXPEDITE_MS)

    def mark_raw_changed(self):
        self._raw_dirty = True

    def perform_autosave(self):
        self._expedite.stop()
        if not RESULTS or DATA_MANAGER.raw_data_result_id is None:
            return  # nothing worth recovering yet

        directory = autosave_dir()
        directory.mkdir(parents=True, exist_ok=True)
        # Rewrite the raw parquet when it changed, and self-heal if the cached copy is missing.
        write_raw = self._raw_dirty or not (directory / "raw.parquet").is_file()
        meta = {
            "version": version,
            "theme": THEME.name(),
            "language": LANGUAGE.language.value,
            # So recovery can offer to Save back to the project's file (the crash may have happened
            # after edits since the last manual save).
            "source_path": self.root_class.current_file_path,
        }
        try:
            write_project_bundle(str(directory), DATA_MANAGER, RESULTS, meta, write_raw=write_raw)
            if write_raw:
                self._raw_dirty = False
        except Exception:
            logging.exception("Autosave failed")

    def has_recoverable(self) -> bool:
        return (autosave_dir() / "project.json").is_file()

    def clear_files(self):
        shutil.rmtree(autosave_dir(), ignore_errors=True)

    def stop(self):
        self._periodic.stop()
        self._expedite.stop()
