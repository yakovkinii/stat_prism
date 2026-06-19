#  Copyright (c) 2023 StatPrism Team. All rights reserved.

import pandas as pd

from src.common.constant import ColumnType
from src.common.decorators import log_function
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.common.utility import unique_name
from src.side_area_panel.modules.dp_preprocess.dp_preprocess_result import PreprocessResult
from src.side_area_panel.modules.dp_preprocess.dp_preprocess_ui import Elements


@log_function
def dp_preprocess_main(elements: Elements, result: PreprocessResult, update):
    cfg = result.config
    data = DATA_MANAGER.get_data_from_data_label(
        data_label=cfg.data_source,
        current_result_id=result.unique_id,
    )
    new_data = data.copy()

    specs = {s["original"]: s for s in (cfg.columns or []) if isinstance(s, dict) and "original" in s}

    # Columns flagged for removal (never remove every column -> that would empty the data).
    remove_names = {name for name, s in specs.items() if s.get("remove")}
    if remove_names and len(remove_names) >= len(new_data.column_names()):
        remove_names = set()

    cast_failed = []  # columns whose Numeric cast left unparseable (non-empty) values as NaN

    assigned = set()
    for col in list(new_data.columns):
        original = col.column_name
        if original in remove_names:
            new_data.remove_column(original)
            continue
        spec = specs.get(original)
        if spec is None:
            assigned.add(original)
            continue

        # 1. Value mapping (keys are the original values; unmapped values pass through).
        mapping = {f: t for f, t in (spec.get("mapping") or [])}
        if mapping:
            col.data_series = col.data_series.map(lambda v: mapping[v] if v in mapping else v)

        # 2. Target type: cast the values now (after mapping), not just at analysis time.
        #    nominal / ordinal -> string labels; numeric -> int when possible, else float.
        try:
            ctype = ColumnType(spec.get("type"))
        except ValueError:
            ctype = col.column_type
        col.column_type = ctype
        col.is_numeric = ctype == ColumnType.NUMERIC
        if ctype == ColumnType.NUMERIC:
            coerced = pd.to_numeric(col.data_series, errors="coerce")
            # Flag if a non-empty value could not be parsed (became NaN) -> outlines the card.
            non_empty = col.data_series.notna() & (col.data_series.astype(str).str.strip() != "")
            if bool((coerced.isna() & non_empty).any()):
                cast_failed.append(original)
            # int when there are no missing values and every value is whole, else float.
            if coerced.notna().all() and bool((coerced == coerced.round()).all()):
                col.data_series = coerced.astype("int64")
                col.column_dtype = "int"
            else:
                col.data_series = coerced
                col.column_dtype = "float"
        else:
            # Keep NaN as NaN; everything else becomes a string label.
            col.data_series = col.data_series.apply(lambda v: v if pd.isna(v) else str(v))
            col.column_dtype = "str"

        # 3. Ordering (ordinal only). The data is now string labels, so the explicit order
        #    (expressed over the mapped values) is stringified to match; missing entries are
        #    auto-filled in natural order.
        if ctype == ColumnType.ORDINAL:
            col.order = {}
            for raw in (spec.get("order") or []):
                value = mapping.get(raw, raw)
                value = value if pd.isna(value) else str(value)
                if value not in col.order:
                    col.order[value] = len(col.order) + 1
            col.automatically_update_order()
        else:
            col.order = {}

        # 4. Rename (kept unique).
        target = (spec.get("new_name") or "").strip() or original
        if target in assigned:
            target = unique_name(target, assigned)
        if target != original:
            col.rename(target)
        assigned.add(target)

        # 5. Colour tag (data-viewer header / column-selector background). None clears it.
        col.color = spec.get("color")

    new_data.update_lookups()
    if cast_failed:
        elements.columns.set_alert(cast_failed)

    result.data = new_data
    return result
