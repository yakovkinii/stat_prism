#  Copyright (c) 2023 StatPrism Team. All rights reserved.
"""Shared helpers for snapshot tests.

Two responsibilities:

  * Build a :class:`~src.data.data.Data` fixture from a plain DataFrame, mirroring
    how real loading attaches the mandatory ``ID`` column.
  * Run a module's ``recalculate_*`` function against that data (the data-source
    singleton is patched so no chain/registry wiring is needed), then compare the
    rendered HTML to an approved benchmark.

Snapshot files live in ``tests/snapshots`` as ``<name>.approved.html`` (the blessed
benchmark) and ``<name>.received.html`` (last output that differed). The review tool
(`tools/snapshot_review.py`) renders these side by side and approves changes.
"""

from pathlib import Path

import pandas as pd

from src.common.constant import ColumnType, ID_COLUMN_NAME
from src.data import data_manager as data_manager_module
from src.data.data import Data

SNAPSHOT_DIR = Path(__file__).resolve().parent / "snapshots"


def make_data(df: pd.DataFrame, add_id: bool = True) -> Data:
    """Build a ``Data`` from a DataFrame. By default attaches an ``ID`` column the
    same way the raw-data loader does, since several modules request it."""
    df = df.copy()
    if add_id and ID_COLUMN_NAME not in df.columns:
        df[ID_COLUMN_NAME] = range(1, len(df) + 1)
    data = Data.initialize_from_dataframe(df)
    if ID_COLUMN_NAME in data.column_names():
        data[ID_COLUMN_NAME].column_type = ColumnType.ID
    return data


def run_main(main_function, result_class, config, data: Data):
    """Construct a result, point the data-source singleton at ``data``, and run the
    module's calculation. Returns the populated result."""
    result = result_class(unique_id=1, settings_panel_index=0, config=config)

    original = data_manager_module.DATA_MANAGER.get_data_from_data_label
    data_manager_module.DATA_MANAGER.get_data_from_data_label = lambda **_: data.copy()
    try:
        return main_function(None, result, lambda *_: None)
    finally:
        data_manager_module.DATA_MANAGER.get_data_from_data_label = original


def assert_snapshot(result, name: str) -> str:
    """Compare ``result.get_html()`` against the approved benchmark.

    * match -> pass (any stale ``.received`` is removed);
    * differs -> write ``.received`` and fail;
    * no benchmark yet -> write ``.received`` and fail (approve it via the tool).
    """
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    html = result.get_html()
    approved = SNAPSHOT_DIR / f"{name}.approved.html"
    received = SNAPSHOT_DIR / f"{name}.received.html"

    if approved.exists() and approved.read_text(encoding="utf-8") == html:
        if received.exists():
            received.unlink()
        return html

    received.write_text(html, encoding="utf-8")
    if not approved.exists():
        raise AssertionError(
            f"No benchmark for '{name}'. Review and approve it in tools/snapshot_review.py."
        )
    raise AssertionError(
        f"Snapshot '{name}' differs from its benchmark. "
        f"Review and approve/fix in tools/snapshot_review.py."
    )
