#  Copyright (c) 2023 StatPrism Team. All rights reserved.

import logging

import numpy as np
import semopy

from src.common.decorators import log_function
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.iispwac.iispwac_path_builder import resolve_factor_labels
from src.side_area_panel.modules.common.prose import prose_enabled
from src.side_area_panel.modules.common.result.html_result import Cell, HTMLTableV2, Row
from src.side_area_panel.modules.common.result.plot_result import FactorDiagram, PlotV2
from src.side_area_panel.modules.common.utility import format_p_apa_exact, format_r_apa, format_statistic_apa, get_stars
from src.side_area_panel.modules.confirmatory_factor_analysis.cfa_semopy import _OBJECTIVE_TO_SEMOPY, OBJECTIVE_ML
from src.side_area_panel.modules.general_sem.general_sem_result import GeneralSEMResult


def _fail(result: GeneralSEMResult, message: str) -> GeneralSEMResult:
    logging.warning("SEM: %s", message)
    result.set_error(message)
    return result


@log_function
def recalculate_general_sem_study(elements, result: GeneralSEMResult, update) -> GeneralSEMResult:
    """Assemble a semopy model from the click-based measurement + structural specification and
    fit it, reporting fit indices and parameter estimates. semopy is fit on safe aliases so real
    (sentence-length) column names cannot break its parser; names are mapped back for display."""
    cfg = result.config
    result.result_elements = []

    structure = cfg.column_selector or []
    n_factors = len(structure)
    factor_labels = resolve_factor_labels(cfg.factor_names, n_factors)
    paths = cfg.paths or []

    # Observed columns needed = all indicators + any observed variables used as path nodes.
    factor_label_set = set(factor_labels)
    observed_needed = []
    for indicators in structure:
        for col in indicators or []:
            if col not in observed_needed:
                observed_needed.append(col)
    for path in paths:
        for node in (path.get("from"), path.get("to")):
            if node and node not in factor_label_set and node not in observed_needed:
                observed_needed.append(node)

    if not observed_needed:
        return _fail(result, "Assign indicators to at least one factor.")

    data = DATA_MANAGER.get_data_from_data_label(data_label=cfg.data_source, current_result_id=result.unique_id)
    df = data.get_dataframe(columns=observed_needed, map_ordinal=True)
    df = df.select_dtypes(include=[np.number]).astype(float).dropna(axis=0)
    if df.shape[0] < 3 or df.shape[1] < 2:
        return _fail(result, "Not enough complete numeric data to fit the model.")
    update(20)

    usable = list(df.columns)
    alias = {col: f"v{k}" for k, col in enumerate(usable)}
    factor_token = {factor_labels[i]: f"F{i + 1}" for i in range(n_factors)}

    def token(node):
        if node in factor_token:
            return factor_token[node]
        return alias.get(node)

    # ----- Measurement model (factors with >= 2 usable indicators) -----
    lines = []
    for i, indicators in enumerate(structure):
        cols = [alias[c] for c in (indicators or []) if c in alias]
        if len(cols) >= 2:
            lines.append(f"F{i + 1} =~ " + " + ".join(cols))
    if not lines:
        return _fail(result, "Define at least one factor with two or more indicators.")

    # ----- Structural paths -----
    # Each row is one from -> to relationship. Regressions to the same outcome are combined into
    # one "to ~ from1 + from2" line; covariances are emitted as "from ~~ to". Two degenerate rows
    # are silently dropped: a self-loop (from == to), and a "factor -> its own indicator"
    # regression, which merely duplicates a loading already in the measurement model above.
    own_indicators = {  # factor label -> set of its assigned indicator columns
        factor_labels[i]: set(indicators or []) for i, indicators in enumerate(structure)
    }
    regressions = {}  # outcome token -> ordered list of predictor tokens
    for path in paths:
        from_node, to_node = path.get("from"), path.get("to")
        if from_node == to_node:  # degenerate self-loop
            continue
        if path.get("type") != "~~" and to_node in own_indicators.get(from_node, set()):
            continue  # duplicate of an existing factor -> indicator loading
        src, dst = token(from_node), token(to_node)
        if not src or not dst:
            continue
        if path.get("type") == "~~":
            lines.append(f"{src} ~~ {dst}")
        else:  # regression
            regressions.setdefault(dst, [])
            if src not in regressions[dst]:
                regressions[dst].append(src)
    for outcome, predictors in regressions.items():
        lines.append(f"{outcome} ~ " + " + ".join(predictors))

    model_desc = "\n".join(lines)
    objective = _OBJECTIVE_TO_SEMOPY.get(cfg.estimator or OBJECTIVE_ML, "MLW")
    try:
        model = semopy.Model(model_desc)
        model.fit(df.rename(columns=alias), obj=objective)
    except Exception as error:
        return _fail(result, f"The model could not be fitted: {error}")
    update(70)

    # Map internal tokens back to the user's factor / column names for display.
    display = {f"F{i + 1}": factor_labels[i] for i in range(n_factors)}
    display.update({a: c for c, a in alias.items()})
    verbal = bool(cfg.verbal_indicators)  # plain-language quality labels / significance stars
    prose = prose_enabled(cfg.interpretation)

    # ----- Fit indices -----
    try:
        stats = semopy.calc_stats(model)
    except Exception as error:  # pragma: no cover - defensive
        logging.warning("SEM: calc_stats failed (%s)", error)
        stats = None
    if stats is not None and not stats.empty:
        fit_table = HTMLTableV2(table_caption="Model fit")
        header = [Cell("Index"), Cell("Value", center=True)]
        if verbal:
            header.append(Cell("Interpretation", center=True))
        fit_table.add_title_row_apa(Row(header))
        row0 = stats.iloc[0]
        for name in stats.columns:
            cells = [Cell(str(name), push_to_left=True), Cell(_fmt(row0[name]), center=True)]
            if verbal:
                cells.append(Cell(_fit_quality(str(name), row0[name]), center=True))
            fit_table.add_single_row_apa(Row(cells))
        if prose:
            fit_table.add_text(_fit_prose(row0))
        result.update_and_add_element(fit_table, "sem fit")

    # ----- Parameter estimates -----
    # Split the rows: directed / covariance paths (the interesting structure) go in the main table;
    # variances (x ~~ x) are housekeeping parameters, so they get their own smaller table below.
    insp = model.inspect(std_est=True)
    has_std = "Est. Std" in insp.columns

    def _is_variance(r) -> bool:
        return r["op"] == "~~" and r["lval"] == r["rval"]

    def _row_cells(r, plain_name=False) -> Row:
        lval = display.get(r["lval"], r["lval"])
        rval = display.get(r["rval"], r["rval"])
        label = lval if plain_name else _path_label(lval, r["op"], rval)
        # With verbal indicators on, append significance stars to the standardized estimate (or the
        # raw estimate when there is no standardized column).
        estimate = _fmt(r.get("Estimate"))
        std = _fmt(r.get("Est. Std")) if has_std else None
        if verbal:
            stars = get_stars(_num(r.get("p-value")))
            if std is not None:
                std += stars
            else:
                estimate += stars
        cells = [
            Cell(label, push_to_left=True),
            Cell(estimate, center=True),
            Cell(_fmt(r.get("Std. Err")), center=True),
            Cell(_p(r.get("p-value")), center=True),
        ]
        if has_std:
            cells.append(Cell(std, center=True))
        return Row(cells)

    def _header(first: str) -> Row:
        cols = [Cell(first), Cell("Estimate", center=True), Cell("SE", center=True), Cell("p", center=True)]
        if has_std:
            cols.append(Cell("Std.", center=True))
        return Row(cols)

    param_table = HTMLTableV2(table_caption="Parameter estimates")
    param_table.add_title_row_apa(_header("Path"))
    for _, r in insp.iterrows():
        if not _is_variance(r):
            param_table.add_single_row_apa(_row_cells(r))
    if verbal:
        param_table.add_text("Stars flag significance of each path: *** p&lt;.001, ** p&lt;.01, * p&lt;.05.")
    if prose:
        param_table.add_text(_param_prose(insp, display, df.shape[0], len(lines)))
    result.update_and_add_element(param_table, "sem parameters")

    # ----- Variances (separate, secondary table) -----
    variance_rows = [r for _, r in insp.iterrows() if _is_variance(r)]
    if variance_rows:
        var_table = HTMLTableV2(table_caption="Variances")
        var_table.add_title_row_apa(_header("Variance"))
        for r in variance_rows:
            var_table.add_single_row_apa(_row_cells(r, plain_name=True))
        if prose:
            var_table.add_text(
                "Each row is an estimated variance. For an observed item it is the residual (error) "
                "variance left over after its factor is accounted for; its standardized value equals "
                "the unexplained proportion (1 − R²), so a smaller value means the factor explains "
                "more of that item. Factor variances are scaling parameters rather than results to "
                "interpret."
            )
        result.update_and_add_element(var_table, "sem variances")

    # ----- Path diagram (measurement loadings + structural paths between factors) -----
    if cfg.plots:
        diagram = _build_path_diagram(insp, display, factor_token, structure, usable, has_std)
        if diagram is not None:
            result.update_and_add_element(
                PlotV2(items=[diagram], plot_title="Path diagram", x_axis_title="", y_axis_title=""),
                "sem path diagram",
            )

    result.title_context = ", ".join(factor_labels[: min(3, n_factors)])
    update(100)
    return result


def _build_path_diagram(insp, display, factor_token, structure, usable, has_std):
    """Assemble a FactorDiagram from the fitted parameters: factor → indicator loadings (from the
    measurement model), factor ↔ factor covariances, and factor → factor structural regressions.
    Paths involving observed variables that are not a factor's own indicator are omitted from the
    schematic (they still appear in the estimates table). Returns None when there is nothing to
    draw."""
    factor_tokens = set(factor_token.values())  # {"F1", "F2", …}
    est_key = "Est. Std" if has_std else "Estimate"

    # Standardized loading per (factor label, indicator column).
    load = {}
    for _, r in insp.iterrows():
        op, lval, rval = r["op"], r["lval"], r["rval"]
        if op not in ("=~", "~"):
            continue
        if lval in factor_tokens and rval not in factor_tokens:
            f_tok, i_tok = lval, rval
        elif rval in factor_tokens and lval not in factor_tokens:
            f_tok, i_tok = rval, lval
        else:
            continue  # factor→factor regression or observed→observed, not a loading
        val = _num(r.get(est_key))
        if val is not None:
            load[(display.get(f_tok, f_tok), display.get(i_tok, i_tok))] = val

    factor_labels = [display.get(t, t) for t in factor_token.values()]
    diagram_factors = []
    for i, label in enumerate(factor_labels):
        indicators = []
        for col in structure[i] if i < len(structure) else []:
            if col not in usable:
                continue
            val = load.get((label, col))
            if val is None:
                continue
            indicators.append((str(col), format_r_apa(val), float(val)))
        if indicators:
            diagram_factors.append((label, indicators))
    if not diagram_factors:
        return None

    # Factor↔factor covariances (undirected) and factor→factor regressions (directed).
    correlations, regressions = [], []
    for _, r in insp.iterrows():
        op, lval, rval = r["op"], r["lval"], r["rval"]
        if lval not in factor_tokens or rval not in factor_tokens or lval == rval:
            continue
        coef = format_r_apa(_num(r.get(est_key)))
        if op == "~~":
            correlations.append((display.get(lval, lval), display.get(rval, rval), coef))
        elif op == "~":  # semopy: outcome ~ predictor -> arrow predictor → outcome
            regressions.append((display.get(rval, rval), display.get(lval, lval), coef))

    return FactorDiagram(
        factors=diagram_factors, correlations=correlations, regressions=regressions, label="Path diagram"
    )


def _path_label(lval, op, rval) -> str:
    """Human-readable label for a semopy parameter row, using arrows instead of the raw
    operators. A variance (``x ~~ x``) is the variable's own variance, so it is labelled as such
    rather than a self-pointing double arrow (its unstandardized estimate is the variance in the
    data's units, which is why it is not 1 — only the standardized column reports 1)."""
    if op == "~~":
        return f"var({lval})" if lval == rval else f"{lval} ↔ {rval}"
    if op == "=~":  # measurement loading: factor → indicator
        return f"{lval} → {rval}"
    if op == "~":  # regression: outcome ← predictor, shown predictor → outcome
        return f"{rval} → {lval}"
    return f"{lval} {op} {rval}"


def _num(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _fit_quality(name: str, value) -> str:
    """Plain-language quality label for a semopy fit-index row (empty for raw statistics like
    χ²/DoF/AIC that have no absolute cutoff)."""
    v = _num(value)
    if v is None:
        return "—"
    key = name.strip().lower()
    if key == "rmsea":
        return "good" if v < 0.05 else "acceptable" if v < 0.08 else "mediocre" if v < 0.10 else "poor"
    if key in ("cfi", "tli", "nfi", "gfi", "agfi"):
        return "excellent" if v >= 0.95 else "acceptable" if v >= 0.90 else "poor"
    if "p-value" in key:  # exact-fit χ² test: non-significant favours the model
        return "good" if v >= 0.05 else "poor"
    return "—"


def _fit_prose(row) -> str:
    """A sentence summarising the global fit from whichever indices semopy reported."""

    def get(*names):
        for n in names:
            if n in row.index:
                return _num(row[n])
        return None

    cfi, tli, rmsea = get("CFI"), get("TLI"), get("RMSEA")
    parts = []
    if cfi is not None:
        parts.append(f"CFI = {_fmt(cfi)} ({_fit_quality('CFI', cfi)})")
    if tli is not None:
        parts.append(f"TLI = {_fmt(tli)} ({_fit_quality('TLI', tli)})")
    if rmsea is not None:
        parts.append(f"RMSEA = {_fmt(rmsea)} ({_fit_quality('RMSEA', rmsea)})")
    if not parts:
        return "The model was estimated; see the indices above for its fit to the data."
    labels = [_fit_quality(n, v) for n, v in (("CFI", cfi), ("TLI", tli), ("RMSEA", rmsea)) if v is not None]
    good = {"good", "acceptable", "excellent"}
    verdict = "acceptable" if labels and all(lbl in good for lbl in labels) else "questionable"
    return (
        "The measurement + structural model reproduces the observed covariances "
        + ("well" if verdict == "acceptable" else "only partially")
        + f" ({', '.join(parts)}). "
        + (
            "Conventional cut-offs (CFI/TLI ≥ .95, RMSEA ≤ .06) suggest a model worth interpreting."
            if verdict == "acceptable"
            else "At least one index falls short of the usual cut-offs, "
            "so interpret the paths with caution and consider revising the model."
        )
    )


def _param_prose(insp, display, n_cases: int, n_equations: int) -> str:
    """A richer description of the structural paths: how many, how many significant, and the
    strongest one, using the standardized solution when available."""
    reg = insp[insp["op"] == "~"] if "op" in insp.columns else insp.iloc[0:0]
    n_paths = len(reg)
    text = (
        f"Fitted a structural equation model on {n_cases} complete cases "
        f"({n_equations} model equation(s), {n_paths} directed path(s)). "
    )
    if n_paths:
        p = reg["p-value"].map(_num) if "p-value" in reg.columns else None
        n_sig = int(sum(1 for v in (p if p is not None else []) if v is not None and v < 0.05))
        text += f"{n_sig} of {n_paths} directed path(s) reached significance (p < .05). "
        est_col = "Est. Std" if "Est. Std" in reg.columns else "Estimate"
        strongest, best = None, -1.0
        for _, r in reg.iterrows():
            mag = abs(_num(r.get(est_col)) or 0.0)
            if mag > best:
                strongest, best = r, mag
        if strongest is not None:
            lval = display.get(strongest["lval"], strongest["lval"])
            rval = display.get(strongest["rval"], strongest["rval"])
            text += (
                f"The strongest effect is {rval} → {lval} "
                f"({'standardized ' if est_col == 'Est. Std' else ''}β = {_fmt(strongest.get(est_col))}). "
            )
    text += "The Std. column gives the standardized solution."
    return text


def _fmt(value) -> str:
    try:
        return format_statistic_apa(float(value))
    except (TypeError, ValueError):
        return "—"


def _p(value) -> str:
    try:
        return format_p_apa_exact(float(value))
    except (TypeError, ValueError):
        return "—"
