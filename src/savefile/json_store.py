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

"""JSON project storage (the successor to the pickle format).

A ``.sp`` is a ZIP. In the JSON form it holds:

* ``meta.json``          -- version / theme / language / ``storage: "json"``;
* ``project.json``       -- the data chain and, per study, its module, title and config (plus any
                            inline filters). Only the *source of truth* is stored;
* ``raw.parquet`` +      -- the imported (raw) dataset: values in parquet, per-column metadata
  ``raw_columns.json``      (type, colour, order, ...) alongside.

Derived studies are NOT stored -- they are recomputed from the raw dataset and the configs on load.
This keeps the file small, safe (no pickled code), and easy to migrate.
"""

import inspect
import json
import logging
import os
import tempfile
import zipfile

import attrs
import numpy as np
import pandas as pd

from src.common.constant import ColumnType
from src.data.data import Data, DataColumn
from src.savefile.versioning import migrate_project
from src.side_area_panel.modules.dp_filter.dp_filter_result import FilterDataStudyConfig
from src.side_area_panel.modules.registry import ModuleRegistry


def _json_default(obj):
    """Let json.dump handle the numpy scalar types that can appear in configs / column orders."""
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Not JSON serializable: {type(obj)}")


def _config_to_dict(config):
    """A study config as a JSON-safe dict. attrs configs use attrs.asdict; a plain-class config
    (e.g. RawDataStudyConfig) keeps its scalar fields but drops any stored DataFrame -- the raw
    values are saved to parquet, not into the config."""
    if attrs.has(type(config)):
        return attrs.asdict(config)
    return {key: value for key, value in vars(config).items() if not isinstance(value, pd.DataFrame)}


def _known_fields(config_class):
    """The field/parameter names a config class accepts, so unknown keys from a newer save (e.g. a
    field added in a later patch) are ignored instead of raising."""
    if attrs.has(config_class):
        return {field.name for field in attrs.fields(config_class)}
    params = inspect.signature(config_class.__init__).parameters
    return {name for name in params if name != "self"}


def backfill_config(config):
    """DEPRECATED SHIM (remove in 1.3.0, once a proper save-file migration exists): fill in attrs
    config fields that an older save predates, so newer code that reads them does not hit an
    AttributeError. Uses each field's own default (None for our configs)."""
    cls = type(config)
    if not attrs.has(cls):
        return config
    for field in attrs.fields(cls):
        if not hasattr(config, field.name):
            default = field.default
            if default is attrs.NOTHING:
                default = None
            elif isinstance(default, attrs.Factory):
                default = default.factory()
            setattr(config, field.name, default)
    return config


def _config_from_dict(config_class, config_dict):
    """Build a config from a saved dict: keep only fields the class knows (forward-compatible with
    newer saves), then backfill any this save predates."""
    known = _known_fields(config_class)
    kwargs = {key: value for key, value in (config_dict or {}).items() if key in known}
    return backfill_config(config_class(**kwargs))


def _serialize_data(data):
    """A raw dataset -> (DataFrame of values, per-column metadata). Columns are keyed positionally
    (c0, c1, ...) so duplicate display names don't collide in the parquet frame."""
    series_map = {}
    columns_meta = []
    for i, column in enumerate(data.columns):
        key = f"c{i}"
        series_map[key] = column.data_series.reset_index(drop=True)
        columns_meta.append(
            {
                "key": key,
                "name": column.column_name,
                "original_name": column.original_name,
                "column_dtype": column.column_dtype,
                "column_type": column.column_type.value,
                "is_numeric": bool(column.is_numeric),
                "inverted": bool(column.inverted),
                "color": column.color,
                # order keys can be int/float/str, so store [value, index] pairs (not a JSON object).
                "order": [[k, v] for k, v in (column.order or {}).items()],
            }
        )
    return pd.DataFrame(series_map), columns_meta


def _deserialize_data(df, columns_meta):
    columns = []
    for meta in columns_meta:
        series = df[meta["key"]].copy()
        series.name = meta["name"]
        order = {k: v for k, v in meta.get("order", [])}
        columns.append(
            DataColumn(
                column_name=meta["name"],
                original_name=meta.get("original_name", meta["name"]),
                data_series=series,
                column_dtype=meta["column_dtype"],
                column_type=ColumnType(meta["column_type"]),
                is_numeric=bool(meta.get("is_numeric", False)),
                inverted=bool(meta.get("inverted", False)),
                color=meta.get("color"),
                order=order,
            )
        )
    return Data(columns)


def save_project_json(file_path, data_manager, results, meta):
    """Write ``results`` + ``data_manager`` to ``file_path`` in the JSON+parquet form."""
    config_to_module_name = {
        module.value.config_class: module.name for module in ModuleRegistry if module.value.config_class is not None
    }

    project = {
        "raw_data_result_id": data_manager.raw_data_result_id,
        "data_chain": list(data_manager.data_chain),
        "results": [],
    }
    raw_df = None
    raw_columns_meta = None

    for result_id, result in results.items():
        module_name = config_to_module_name.get(type(result.config))
        if module_name is None:
            logging.warning("Skipping study with unknown config %s while saving", type(result.config))
            continue
        entry = {
            "id": result_id,
            "module": module_name,
            "title": getattr(result, "title", ""),
            "title_context": getattr(result, "title_context", ""),
            "config": _config_to_dict(result.config),
        }
        inline_filters = getattr(result, "inline_filters", None)
        if inline_filters:
            entry["inline_filters"] = [attrs.asdict(f) for f in inline_filters]
        project["results"].append(entry)

        if result_id == data_manager.raw_data_result_id and getattr(result, "data", None) is not None:
            raw_df, raw_columns_meta = _serialize_data(result.data)

    stored_meta = {**meta, "storage": "json"}
    with tempfile.TemporaryDirectory() as temp_dir:
        with open(f"{temp_dir}/meta.json", "w", encoding="utf-8") as file:
            json.dump(stored_meta, file, ensure_ascii=False, indent=2)
        with open(f"{temp_dir}/project.json", "w", encoding="utf-8") as file:
            json.dump(project, file, ensure_ascii=False, indent=2, default=_json_default)
        members = ["meta.json", "project.json"]
        if raw_columns_meta:
            raw_df.to_parquet(f"{temp_dir}/raw.parquet")
            with open(f"{temp_dir}/raw_columns.json", "w", encoding="utf-8") as file:
                json.dump(raw_columns_meta, file, ensure_ascii=False, indent=2, default=_json_default)
            members += ["raw.parquet", "raw_columns.json"]
        with zipfile.ZipFile(file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for member in members:
                zipf.write(f"{temp_dir}/{member}", member)


def load_project_json(temp_dir, file_version=None):
    """Rebuild study objects from an extracted JSON project directory. Returns
    ``(results_by_id, raw_data_result_id, data_chain)``. Derived studies come back empty and must be
    recomputed by the caller; the raw study's data is restored from parquet. The project dict is
    first run through any version migrations."""
    with open(f"{temp_dir}/project.json", encoding="utf-8") as file:
        project = json.load(file)

    project = migrate_project(project, file_version)

    raw_data_result_id = project.get("raw_data_result_id")
    data_chain = project.get("data_chain") or []

    raw_data = None
    raw_columns_path = f"{temp_dir}/raw_columns.json"
    raw_parquet_path = f"{temp_dir}/raw.parquet"
    if os.path.exists(raw_parquet_path) and os.path.exists(raw_columns_path):
        df = pd.read_parquet(raw_parquet_path)
        with open(raw_columns_path, encoding="utf-8") as file:
            raw_columns_meta = json.load(file)
        raw_data = _deserialize_data(df, raw_columns_meta)

    modules_by_name = {module.name: module.value for module in ModuleRegistry}
    results = {}
    for entry in project.get("results", []):
        module = modules_by_name.get(entry.get("module"))
        if module is None:
            logging.warning("Skipping study with unknown module %s while loading", entry.get("module"))
            continue
        result_id = entry["id"]
        config = _config_from_dict(module.config_class, entry.get("config"))
        result = module.result_class(
            unique_id=result_id,
            settings_panel_index=module.settings_stacked_widget_index,
            config=config,
        )
        result.title = entry.get("title", result.title)
        result.title_context = entry.get("title_context", getattr(result, "title_context", ""))
        inline_filters = entry.get("inline_filters")
        if inline_filters:
            result.inline_filters = [_config_from_dict(FilterDataStudyConfig, f) for f in inline_filters]
        if result_id == raw_data_result_id and raw_data is not None:
            result.data = raw_data
        results[result_id] = result

    return results, raw_data_result_id, data_chain
