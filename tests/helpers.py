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
from unittest.mock import MagicMock

import pandas as pd

from src.common.constant import ColumnType, ID_COLUMN_NAME
from src.data import data_manager as data_manager_module
from src.data.data import Data
from src.side_area_panel.modules.raw_data.raw_data_result import RawDataStudyConfig
from src.side_area_panel.modules.raw_data.raw_data_ui import RawData

SNAPSHOT_DIR = Path(__file__).resolve().parent / "snapshots"
DATA_DIR = Path(__file__).resolve().parent / "data"


def load_dataset(name: str, ordinal: dict = None) -> Data:
    """Load a fixture Excel file into a ``Data`` through the program's own reader, so
    the test sees exactly what StatPrism produces from that file (type inference, the
    mandatory first-position ID column, etc.) -- no special test-side handling.

    ``ordinal`` optionally promotes columns to ORDINAL with a given category order
    (representing the user's manual "mark as ordinal" action, which is not part of
    loading), e.g. ``{COL_EDUCATION: ["High school", "Bachelor", "Master", "PhD"]}``.
    """
    path = DATA_DIR / f"{name}.xlsx"
    if not path.exists():
        raise FileNotFoundError(
            f"Missing fixture {path}. Run _GEN_TEST_DATA.bat (tests/generate_fixtures.py) first."
        )
    dataframe = pd.read_excel(path)
    config = RawDataStudyConfig(dataframe=dataframe, path=str(path), timestamp="", header_colors={})
    # _build_data does not use `self`; call it directly to run the real reader logic.
    data = RawData._build_data(None, config)
    for column_name, order in (ordinal or {}).items():
        column = data[column_name]
        column.column_type = ColumnType.ORDINAL
        column.is_numeric = False
        column.order = {value: index for index, value in enumerate(order)}
    return data


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
    module's calculation. Returns the populated result.

    ``elements`` is a stub: analysis modules don't read it, and DP modules only touch
    it to flash an input alert on the error path (``elements.column_selector.set_alert``),
    so a MagicMock keeps both paths working without a real UI."""
    result = result_class(unique_id=1, settings_panel_index=0, config=config)

    original = data_manager_module.DATA_MANAGER.get_data_from_data_label
    data_manager_module.DATA_MANAGER.get_data_from_data_label = lambda **_: data.copy()
    try:
        return main_function(MagicMock(), result, lambda *_: None)
    finally:
        data_manager_module.DATA_MANAGER.get_data_from_data_label = original


def data_to_html(data: Data) -> str:
    """Render a ``Data`` to HTML for snapshotting: a column-metadata table (so type /
    dtype / colour changes are caught, not just values) followed by the data itself.
    Used for DP modules, whose real output is ``result.data`` rather than result HTML."""
    rows = []
    for col in data.columns:
        col_type = getattr(col.column_type, "name", str(col.column_type))
        rows.append(
            "<tr>"
            f"<td>{col.column_name}</td>"
            f"<td>{col_type}</td>"
            f"<td>{col.column_dtype}</td>"
            f"<td>{col.color or ''}</td>"
            "</tr>"
        )
    meta = (
        "<table border='1' cellspacing='0' cellpadding='4'>"
        "<tr><th>column</th><th>type</th><th>dtype</th><th>color</th></tr>"
        + "".join(rows)
        + "</table>"
    )
    df = data.get_dataframe()
    return f"<h3>Columns</h3>{meta}<h3>Data</h3>{df.to_html()}"


def _assert_html(html: str, name: str) -> str:
    """Compare ``html`` against the approved benchmark.

    * match -> pass (any stale ``.received`` is removed);
    * differs -> write ``.received`` and fail;
    * no benchmark yet -> write ``.received`` and fail (approve it via the tool).
    """
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
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


def assert_snapshot(result, name: str) -> str:
    """Snapshot an analysis module's rendered result (``result.get_html()``)."""
    return _assert_html(result.get_html(), name)


def assert_data_snapshot(result, name: str) -> str:
    """Snapshot a DP module's transformed data (``result.data`` -> HTML)."""
    return _assert_html(data_to_html(result.data), name)
