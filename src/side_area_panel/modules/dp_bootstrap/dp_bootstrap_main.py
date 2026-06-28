#  Copyright (c) 2023 StatPrism Team. All rights reserved.

import logging
import math

import numpy as np
import pandas as pd

from src.common.constant import ColumnType
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
    mu = (
        mu_override
        if mu_override is not None
        else (float(np.mean(existing_codes)) if existing_codes else float(codes.mean()))
    )
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


def _parse_coefficient(text):
    """Desired correlation coefficient, clamped just inside (-1, 1). Blank / unparsable -> 0."""
    value = _parse_float(text)
    if value is None:
        return 0.0
    return max(-0.999, min(0.999, value))


def _sort_key(column):
    """A sort key that orders a column's values for rank-matching: numerically for numeric
    columns, by category code for ordinal, and by label for nominal. Missing values sort last."""
    if column.column_type == ColumnType.NUMERIC or column.is_numeric:

        def key(v):
            try:
                f = float(v)
            except (TypeError, ValueError):
                return (1, 0.0)
            return (1, 0.0) if math.isnan(f) else (0, f)

        return key
    if column.column_type == ColumnType.ORDINAL:
        order = column.order or {}

        def key(v):
            return (1, 0) if _is_missing(v) else (0, order.get(v, 0))

        return key

    def key(v):
        return (1, "") if _is_missing(v) else (0, str(v))

    return key


def _is_missing(v):
    try:
        return bool(pd.isna(v))
    except (TypeError, ValueError):
        return False


def _build_latent(n, target_latent, rho, rng):
    """A latent standard-normal vector. With a target latent and non-zero rho, it is blended
    toward the target by rho (Gaussian copula): rho*target + sqrt(1-rho^2)*noise."""
    noise = rng.standard_normal(n)
    if target_latent is None or rho == 0.0:
        return noise
    return rho * target_latent + math.sqrt(max(0.0, 1.0 - rho * rho)) * noise


def _rank_match(values, latent, key):
    """Reorder `values` (a column's marginal draws) so their ranks follow `latent`'s ranks.
    Preserves the multiset of values exactly while inducing the copula's rank correlation."""
    n = len(values)
    if n == 0:
        return values
    latent_ranks = np.argsort(np.argsort(latent))  # 0..n-1 rank for each row
    sorted_vals = sorted(values, key=key)
    return [sorted_vals[latent_ranks[i]] for i in range(n)]


def _code_new_rows(column, n):
    """Numeric coding of the last `n` (new) rows, for measuring realized correlation."""
    values = column.data_series.tolist()[-n:]
    series = pd.Series(values)
    if column.column_type == ColumnType.NUMERIC or column.is_numeric:
        return pd.to_numeric(series, errors="coerce")
    if column.column_type == ColumnType.ORDINAL and column.order:
        return pd.to_numeric(series.map(column.order), errors="coerce")
    # Nominal: code by the SAME ordering rank-matching used to induce the correlation
    # (alphabetical by label, matching _sort_key) -- not pd.factorize's first-appearance
    # order, which disagrees with it and would flip the measured sign.
    uniques = sorted(series.dropna().unique(), key=lambda v: str(v))
    rank_of = {v: float(i) for i, v in enumerate(uniques)}
    return series.map(rank_of)


def _safe_spearman(x, y):
    frame = pd.DataFrame(
        {
            "x": pd.to_numeric(x, errors="coerce").reset_index(drop=True),
            "y": pd.to_numeric(y, errors="coerce").reset_index(drop=True),
        }
    ).dropna()
    if len(frame) < 3 or frame["x"].nunique() < 2 or frame["y"].nunique() < 2:
        return None
    from scipy.stats import spearmanr

    r, _ = spearmanr(frame["x"], frame["y"])
    if r is None or (isinstance(r, float) and math.isnan(r)):
        return None
    return float(r)


def _realized_correlation_lines(new_data, ordered_selected, targets, n):
    """Description lines reporting the realized rank correlation on the new rows, plus
    warnings where the achieved value is far from the requested one."""
    lines = []
    warnings = []
    for name in ordered_selected:
        target, rho = targets.get(name, (None, 0.0))
        if target is None or rho == 0.0 or target not in new_data.column_names():
            continue
        r = _safe_spearman(_code_new_rows(new_data[name], n), _code_new_rows(new_data[target], n))
        if r is None:
            warnings.append(
                f"{name} ↔ {target}: requested ρ = {rho:g}, "
                f"but the correlation could not be measured (too few distinct values)."
            )
            continue
        lines.append(f"{name} ↔ {target}: requested ρ = {rho:g}, realized ≈ {r:.2f}")
        if abs(r - rho) > 0.25:
            warnings.append(
                f"{name} ↔ {target}: realized ρ ({r:.2f}) is far from the requested {rho:g}; "
                f"the marginal or category structure may make this hard to achieve."
            )
    out = []
    if lines:
        out.append("<b>Realized correlations (new rows):</b>")
        out.extend(lines)
    if warnings:
        out.append("<b>⚠ Warnings:</b>")
        out.extend(warnings)
    return out


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
    result.realized_lines = []
    result.update_description()

    n = int(cfg.n_rows or 0)
    if n <= 0:
        return result

    seed = int(cfg.seed or 0)
    rng = np.random.default_rng(seed)

    selector = cfg.column_selector or []
    names = set(new_data.column_names())
    regular = [c for c in (selector[0] if len(selector) > 0 and selector[0] else []) if c in names]
    drivers = [c for c in (selector[1] if len(selector) > 1 and selector[1] else []) if c in names]
    reference_list = [c for c in (selector[2] if len(selector) > 2 and selector[2] else []) if c in names]
    reference = reference_list[0] if reference_list else None

    # Sampling / dependency order: reference first, then drivers, then the regular columns.
    ordered_selected = ([reference] if reference else []) + drivers + regular
    selected_set = set(ordered_selected)
    valid_targets = ([reference] if reference else []) + drivers

    specs_by_col = {s["column"]: s for s in (cfg.column_configs or []) if isinstance(s, dict) and "column" in s}

    # 1. Draw each selected column's marginal sample independently (existing logic).
    drawn = {}
    introduced = {}
    for name in ordered_selected:
        column = new_data[name]
        spec = specs_by_col.get(name) or {"column": name}
        values, introduced[name] = _generate_values(column, spec, n, rng)
        drawn[name] = values

    # 2. Build a correlated latent normal per column, in dependency order, and record each
    #    column's resolved (target, rho) for the realized-correlation report.
    latent = {}
    targets = {}
    for name in ordered_selected:
        spec = specs_by_col.get(name) or {}
        if name == reference:
            target, rho = None, 0.0
        elif name in drivers:
            target = reference
            rho = _parse_coefficient(spec.get("coefficient")) if reference else 0.0
        else:  # regular column
            target = spec.get("target") if spec.get("target") in valid_targets else None
            rho = _parse_coefficient(spec.get("coefficient")) if target else 0.0
        targets[name] = (target, rho)
        latent[name] = _build_latent(n, latent.get(target), rho, rng)

    # 3. Reorder each column's marginal draws to follow its latent (induce the correlation).
    for name in ordered_selected:
        drawn[name] = _rank_match(drawn[name], latent[name], _sort_key(new_data[name]))

    # 4. Append the new rows to every column.
    for column in new_data.columns:
        name = column.column_name
        old_values = column.data_series.tolist()
        if column.column_type == ColumnType.ID:
            new_values = _new_id_values(column.data_series, n)
        elif name in selected_set:
            new_values = drawn[name]
        else:
            new_values = [_na_for(column)] * n
        _rebuild_series(column, old_values + list(new_values))

    new_data.update_lookups()

    # Reset an ordinal column's category order only when a custom list introduced new
    # values; otherwise just integrate any unseen categories while preserving the order.
    for name in ordered_selected:
        column = new_data[name]
        if column.column_type == ColumnType.ORDINAL and introduced.get(name):
            column.order = {}
            column.automatically_update_order()
        elif column.column_type in (ColumnType.ORDINAL, ColumnType.NOMINAL):
            column.automatically_update_order()

    result.data = new_data
    result.realized_lines = _realized_correlation_lines(new_data, ordered_selected, targets, n)
    result.update_description()
    logging.info("Bootstrap: added %d rows across %d columns", n, len(ordered_selected))
    return result
