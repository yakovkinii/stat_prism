#  Copyright (c) 2023 StatPrism Team. All rights reserved.

import logging

import numpy as np
import pandas as pd

from src.common.constant import ColumnType, ID_COLUMN_NAME
from src.common.decorators import log_function
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.dp_bootstrap.dp_bootstrap_result import BootstrapResult
from src.side_area_panel.modules.dp_bootstrap.dp_bootstrap_ui import Elements


def _parse_float(text):
    try:
        return float(text)
    except (TypeError, ValueError):
        return None


def _parse_custom_values(raw, numeric):
    """Parse the comma-separated custom value list. For numeric columns numeric-looking
    tokens are converted to int/float; everything else stays a string."""
    tokens = [tok.strip() for tok in (raw or "").split(",")]
    tokens = [tok for tok in tokens if tok != ""]
    if not numeric:
        return tokens
    out = []
    for tok in tokens:
        try:
            num = float(tok)
            out.append(int(num) if num.is_integer() else num)
        except ValueError:
            out.append(tok)
    return out


def _sigma_or_default(value, fallback):
    if value is None or not np.isfinite(value) or value <= 0:
        return fallback if (fallback is not None and np.isfinite(fallback) and fallback > 0) else 1.0
    return value


def _generate_values(column, spec, n, rng):
    """Return (values_list, introduced_new) for `n` synthetic rows of `column` per `spec`."""
    series = column.data_series
    existing = series.dropna()
    numeric = bool(column.is_numeric) or column.column_type == ColumnType.NUMERIC
    source = spec.get("value_source", "existing")
    distribution = spec.get("distribution", "empirical")

    if source == "custom":
        pool = _parse_custom_values(spec.get("custom_values"), numeric)
        introduced_new = any(v not in set(existing.unique().tolist()) for v in pool)
    else:
        pool = existing.unique().tolist()
        introduced_new = False

    # Nothing to draw from -> leave the new rows empty.
    if len(existing) == 0 and not pool:
        return [np.nan] * n, introduced_new

    if distribution == "normal" and column.column_type in (ColumnType.NUMERIC, ColumnType.ORDINAL):
        values = _generate_normal(column, spec, pool, existing, n, rng)
        return values, introduced_new

    if not pool:
        return [np.nan] * n, introduced_new

    if distribution == "empirical":
        if source == "existing":
            draw = rng.choice(np.asarray(existing.tolist(), dtype=object), size=n)
        else:
            counts = existing.value_counts()
            weights = np.array([float(counts.get(v, 0)) for v in pool], dtype=float)
            if weights.sum() <= 0:
                weights = None
            else:
                weights = weights / weights.sum()
            draw = rng.choice(np.asarray(pool, dtype=object), size=n, p=weights)
    else:  # uniform
        draw = rng.choice(np.asarray(pool, dtype=object), size=n)

    return [_to_python(v) for v in draw], introduced_new


def _generate_normal(column, spec, pool, existing, n, rng):
    """Normal-distributed synthetic values. Numeric columns get continuous draws; ordinal
    columns draw in the category-code space and snap to the nearest available category."""
    mu_override = _parse_float(spec.get("mu"))
    sigma_override = _parse_float(spec.get("sigma"))

    if column.column_type == ColumnType.NUMERIC:
        base = pd.to_numeric(existing, errors="coerce").dropna()
        mu = mu_override if mu_override is not None else (float(base.mean()) if len(base) else 0.0)
        sigma = _sigma_or_default(sigma_override, float(base.std()) if len(base) > 1 else None)
        draw = rng.normal(mu, sigma, n)
        if column.column_dtype == "int":
            return [int(round(v)) for v in draw]
        return [float(v) for v in draw]

    # Ordinal: work in the order-code space, snap back to a real category.
    order = column.order or {}
    if spec.get("value_source") == "custom":
        candidates = [v for v in pool if v in order]
    else:
        candidates = [v for v in existing.unique().tolist() if v in order]
    if not candidates:
        candidates = list(order.keys())
    if not candidates:
        # No usable categories -> fall back to uniform over whatever pool exists.
        return [_to_python(v) for v in rng.choice(np.asarray(pool or [np.nan], dtype=object), size=n)]

    code_of = {v: order[v] for v in candidates}
    codes = np.array(sorted(code_of.values()), dtype=float)
    code_to_value = {order[v]: v for v in candidates}

    existing_codes = [order[v] for v in existing.tolist() if v in order]
    mu = mu_override if mu_override is not None else (float(np.mean(existing_codes)) if existing_codes else float(codes.mean()))
    sigma = _sigma_or_default(sigma_override, float(np.std(existing_codes)) if len(existing_codes) > 1 else None)

    draw = rng.normal(mu, sigma, n)
    out = []
    for value in draw:
        nearest = codes[int(np.argmin(np.abs(codes - value)))]
        out.append(code_to_value[nearest])
    return out


def _new_id_values(series, n):
    """Fresh unique identifiers for the new rows, continuing the existing scheme."""
    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.notna().all() and len(numeric) > 0:
        start = int(numeric.max()) + 1
        return list(range(start, start + n))
    existing = set(series.astype(str).tolist())
    out = []
    i = 1
    while len(out) < n:
        candidate = f"boot_{i}"
        if candidate not in existing:
            out.append(candidate)
            existing.add(candidate)
        i += 1
    return out


def _na_for(column):
    """An empty value consistent with the column dtype."""
    return "" if column.column_dtype == "str" else np.nan


def _to_python(value):
    return value.item() if hasattr(value, "item") else value


def _rebuild_series(column, new_full_values):
    """Replace a column's series with the extended values, keeping a clean index and a
    dtype consistent with the original where possible."""
    series = pd.Series(new_full_values, name=column.column_name)
    if column.column_dtype == "str":
        series = series.where(series.notna(), "").astype(str)
    elif column.column_dtype == "int":
        # NaN cannot live in an int series; only re-narrow when none were introduced,
        # otherwise widen the column's recorded dtype to float to stay consistent.
        if not series.isna().any():
            try:
                series = series.astype(int)
            except (ValueError, TypeError):
                series = pd.to_numeric(series, errors="coerce")
                column.column_dtype = "float"
        else:
            series = pd.to_numeric(series, errors="coerce")
            column.column_dtype = "float"
    elif column.column_dtype == "float":
        series = pd.to_numeric(series, errors="coerce")
    column.data_series = series


@log_function
def dp_bootstrap_main(elements: Elements, result: BootstrapResult, update):
    cfg = result.config
    data = DATA_MANAGER.get_data_from_data_label(
        data_label=cfg.data_source,
        current_result_id=result.unique_id,
    )
    new_data = data.copy()
    # Default to a pass-through so downstream stays valid while inputs are incomplete.
    result.data = new_data

    n = int(cfg.n_rows or 0)
    if n <= 0:
        return result

    seed = int(cfg.seed or 0)
    rng = np.random.default_rng(seed)

    selected = list(cfg.column_selector[0]) if cfg.column_selector else []
    selected = [c for c in selected if c in new_data.column_names()]
    specs_by_col = {
        s["column"]: s for s in (cfg.column_configs or []) if isinstance(s, dict) and "column" in s
    }

    introduced = {}  # column_name -> bool
    for column in new_data.columns:
        name = column.column_name
        old_values = column.data_series.tolist()

        if column.column_type == ColumnType.ID:
            new_values = _new_id_values(column.data_series, n)
        elif name in selected:
            spec = specs_by_col.get(name) or {"column": name}
            new_values, introduced[name] = _generate_values(column, spec, n, rng)
        else:
            new_values = [_na_for(column)] * n

        _rebuild_series(column, old_values + list(new_values))

    new_data.update_lookups()

    # Reset an ordinal column's category order only when a custom list introduced new
    # values; otherwise just integrate any unseen categories while preserving the order.
    for name in selected:
        column = new_data[name]
        if column.column_type == ColumnType.ORDINAL and introduced.get(name):
            column.order = {}
            column.automatically_update_order()
        elif column.column_type in (ColumnType.ORDINAL, ColumnType.NOMINAL):
            column.automatically_update_order()

    result.data = new_data
    logging.info("Bootstrap: added %d rows across %d columns", n, len(selected))
    return result
