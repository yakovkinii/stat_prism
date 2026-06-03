#  Copyright (c) 2023 StatPrism Team. All rights reserved.

from src.common.constant import ColumnType
from src.common.decorators import log_function
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.common.utility import unique_name
from src.side_area_panel.modules.dp_preprocess.dp_preprocess_result import PreprocessResult
from src.side_area_panel.modules.dp_preprocess.dp_preprocess_ui import Elements


@log_function
def dp_preprocess_main(elements: Elements, result: PreprocessResult):
    cfg = result.config
    data = DATA_MANAGER.get_data_from_data_label(
        data_label=cfg.data_source,
        current_result_id=result.unique_id,
    )
    new_data = data.copy()

    specs = {s["original"]: s for s in (cfg.columns or []) if isinstance(s, dict) and "original" in s}

    assigned = set()
    for col in list(new_data.columns):
        original = col.column_name
        spec = specs.get(original)
        if spec is None:
            assigned.add(original)
            continue

        # 1. Value mapping (keys are the original values; unmapped values pass through).
        mapping = {f: t for f, t in (spec.get("mapping") or [])}
        if mapping:
            col.data_series = col.data_series.map(lambda v: mapping[v] if v in mapping else v)

        # 2. Target type.
        try:
            ctype = ColumnType(spec.get("type"))
        except ValueError:
            ctype = col.column_type
        col.column_type = ctype
        col.is_numeric = ctype == ColumnType.NUMERIC

        # 3. Ordering (ordinal only); explicit order is expressed over mapped values.
        if ctype == ColumnType.ORDINAL:
            col.order = {}
            for value in (mapping.get(v, v) for v in (spec.get("order") or [])):
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

    new_data.update_lookups()
    result.data = new_data
    return result
