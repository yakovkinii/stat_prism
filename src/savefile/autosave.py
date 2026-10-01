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


import json
import logging
import os
import shutil
from pathlib import Path

from PySide6.QtCore import QTimer

from src.about import version
from src.common.languages import LANGUAGE
from src.common.theme import THEME
from src.data.data_manager import DATA_MANAGER
from src.savefile.json_store import build_project_dict, write_project_files, write_raw_files
from src.side_area_panel.blueprint.registry import PanelRegistry
from src.side_area_panel.modules.common.result.registry import RESULTS


def autosave_dir() -> Path:
    # A single rolling snapshot of the current session, in the per-user app-data folder (the same
    # place the launcher writes its log). The user never sees it; it exists only so a crash can be
    # recovered. One slot, not per-project -- it is always "the last session".
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    return Path(base) / "StatPrism" / "autosave"


# Owns two things built on the same compact snapshots (chain + configs in project.json, the raw
# dataset in a shared parquet):
#   * crash recovery -- the newest snapshot is left on disk; a clean exit clears it, so a snapshot
#     present at the next start means the previous session crashed;
#   * undo / redo -- an in-memory ring of snapshots. Any change schedules a snapshot after a short
#     debounce (extended while the user keeps editing, so a burst becomes one step). Undo/redo
#     rewrites project.json to the chosen snapshot and reloads it. The raw dataset is one "epoch":
#     changing it (import / open) clears the history and starts a new baseline.
class AutoSaveManager:
    PERIODIC_MS = 5 * 60 * 1000
    DEBOUNCE_MS = 2 * 1000
    MAX_HISTORY = 100

    def __init__(self, root_class):
        self.root_class = root_class
        # The raw dataset only changes on import / project open; track that so the heavy parquet is
        # rewritten only then, not on every snapshot.
        self._raw_dirty = True
        # Undo/redo ring: (project dict, comparison key) pairs, _index pointing at the shown state.
        self._history = []
        self._index = -1
        # True while a snapshot is being reloaded, so the reload's own edits don't push a snapshot.
        self._restoring = False

        self._periodic = QTimer(root_class)
        self._periodic.setInterval(self.PERIODIC_MS)
        self._periodic.timeout.connect(self.perform_autosave)
        self._debounce = QTimer(root_class)
        self._debounce.setSingleShot(True)
        self._debounce.timeout.connect(self.perform_autosave)

        # Autosave / crash recovery is always on (there is no user switch); the periodic timer runs
        # until the window closes, and its active state doubles as "autosave is running".
        self._periodic.start()

    def notify_changed(self):
        # A change happened: (re)start the debounce so the snapshot fires ~DEBOUNCE_MS after the last
        # change (a burst of edits coalesces into one undo step). No-op while a snapshot is being
        # restored, or after the window has closed (timers stopped).
        if self._restoring or not self._periodic.isActive():
            return
        self._debounce.start(self.DEBOUNCE_MS)

    def mark_raw_changed(self):
        # A new raw dataset is a new undo epoch: rewrite the parquet and reset the history baseline.
        self._raw_dirty = True
        self.reset_history()

    def reset_history(self):
        self._history = []
        self._index = -1
        self._debounce.stop()
        # Seed the baseline (index 0) synchronously so the first edit is undoable back to the loaded
        # state, and lay down this epoch's raw parquet so undo/redo can reload without it.
        self.perform_autosave()

    def _meta(self) -> dict:
        return {
            "version": version,
            "theme": THEME.name(),
            "language": LANGUAGE.language.value,
            # So crash recovery can offer to Save back to the project's file.
            "source_path": self.root_class.current_file_path,
        }

    def perform_autosave(self):
        self._debounce.stop()
        if self._restoring:
            return
        if not self._periodic.isActive():
            return  # autosave disabled (the periodic timer tracks the enabled state)
        if not RESULTS or DATA_MANAGER.raw_data_result_id is None:
            return  # nothing worth recovering / undoing yet

        project = build_project_dict(DATA_MANAGER, RESULTS)
        # default=str keeps the key robust against non-JSON values (Path, numpy) that could appear in
        # a config; it is only used to detect "did anything change", never persisted.
        key = json.dumps(project, sort_keys=True, default=str)
        if self._history and self._history[self._index][1] == key:
            return  # no real change since the last snapshot

        # New snapshot: drop any redo tail, append, and cap the ring.
        del self._history[self._index + 1 :]
        self._history.append((project, key))
        if len(self._history) > self.MAX_HISTORY:
            self._history.pop(0)
        self._index = len(self._history) - 1

        self._write_disk(project, write_raw=self._raw_dirty)

    def _write_disk(self, project, write_raw):
        directory = autosave_dir()
        try:
            directory.mkdir(parents=True, exist_ok=True)
            write_project_files(str(directory), project, self._meta())
            # Rewrite the raw parquet when it changed, and self-heal if the cached copy is missing.
            if write_raw or not (directory / "raw.parquet").is_file():
                if write_raw_files(str(directory), DATA_MANAGER, RESULTS):
                    self._raw_dirty = False
        except Exception:
            logging.exception("Autosave failed")

    def can_undo(self) -> bool:
        return self._index > 0

    def can_redo(self) -> bool:
        return 0 <= self._index < len(self._history) - 1

    def undo(self):
        if not self.can_undo():
            return
        self._index -= 1
        self._restore(self._history[self._index][0])

    def redo(self):
        if not self.can_redo():
            return
        self._index += 1
        self._restore(self._history[self._index][0])

    def _restore(self, project):
        # Lay the chosen snapshot down as project.json (the epoch's raw parquet is already on disk),
        # then reload the session from it. Guarded so the reload's mark_dirty calls don't snapshot.
        self._restoring = True
        try:
            directory = autosave_dir()
            directory.mkdir(parents=True, exist_ok=True)
            write_project_files(str(directory), project, self._meta())
            PanelRegistry.HOME_INITIAL.ui_instance.restore_snapshot_from_autosave()
        except Exception:
            logging.exception("Undo/redo restore failed")
        finally:
            self._restoring = False
            self._debounce.stop()  # cancel any snapshot the reload's edits scheduled

    def has_recoverable(self) -> bool:
        return (autosave_dir() / "project.json").is_file()

    def clear_files(self):
        shutil.rmtree(autosave_dir(), ignore_errors=True)

    def stop(self):
        self._periodic.stop()
        self._debounce.stop()
