#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import logging

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.stattools import durbin_watson

from src.common.decorators import log_function
from src.common.qcolor import Colors
from src.common.translations import t
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.common.prose import prose_enabled
from src.side_area_panel.modules.common.result.html_result import Cell, HTMLTableV2, Row
from src.side_area_panel.modules.common.result.plot_result import (
    Band,
    BandPlotConfig,
    Line,
    LinePlotConfig,
    MediationDiagram,
    PlotV2,
    Scatter,
)
from src.side_area_panel.modules.common.utility import (
    format_p_apa_exact,
    format_p_apa_full,
    format_r_apa,
    format_statistic_apa,
    format_value_apa,
    smart_comma_join,
)
from src.side_area_panel.modules.common.verbal.significance import significance_verbal
from src.side_area_panel.modules.regression.constant import RegressionModelType
from src.side_area_panel.modules.regression.regression_result import RegressionResult, RegressionStudyConfig


def _fail(result: RegressionResult, message: str) -> RegressionResult:
    """Show a validation message to the user and log it, then stop."""
    logging.warning("Regression: %s", message)
    result.set_error(message)
    return result


def _format_effect(value) -> str:
    """Like format_statistic_apa, but keeps small effects legible: an indirect effect a·b can be
    a product of two small coefficients (e.g. .37 × .01 = .0037) that the usual 2-decimal rounding
    would collapse to .00. For |value| < .01 (but non-zero) fall back to 2 significant figures."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return format_statistic_apa(value)
    if v != 0 and abs(v) < 0.01:
        return f"{v:.2g}"
    return format_statistic_apa(v)


def _coefficient_table(model, dependent_sd, show_std, verbal, x, caption, intercept_label):
    """Coefficients table: B, SE, optional standardised beta, t, p, optional Significant?.
    `x` is the design matrix (for predictor SDs in the standardised beta)."""
    table = HTMLTableV2(table_caption=caption)

    header = [
        Cell(),
        Cell(t("regression.col.b"), center=True),
        Cell(t("regression.col.se"), center=True),
    ]
    if show_std:
        header.append(Cell(t("regression.col.beta"), center=True))
    header += [Cell(t("regression.col.t"), center=True), Cell(t("common.p_value"), center=True)]
    if verbal:
        header.append(Cell(t("verbal.col_significant"), center=True))
    table.add_title_row_apa(Row(header))

    for param in model.params.index:
        b = model.params[param]
        p = model.pvalues[param]
        name = intercept_label if param == "const" else param
        cells = [
            Cell(name, push_to_left=True),
            Cell(format_statistic_apa(b), center=True),
            Cell(format_statistic_apa(model.bse[param]), center=True),
        ]
        if show_std:
            if param == "const":
                beta_str = "—"
            else:
                sd_x = x[param].std()
                beta_str = format_r_apa(b * sd_x / dependent_sd) if (dependent_sd and sd_x) else "—"
            cells.append(Cell(beta_str, center=True))
        cells += [
            Cell(format_statistic_apa(model.tvalues[param]), center=True),
            Cell(format_p_apa_exact(p), center=True),
        ]
        if verbal:
            cells.append(Cell(significance_verbal(p), center=True))
        table.add_single_row_apa(Row(cells))

    return table


def _vif_key(vif: float) -> str:
    if np.isnan(vif):
        return "low"
    if vif >= 10:
        return "high"
    if vif >= 5:
        return "moderate"
    return "low"


def _add_vif_table(result, x, verbal, prose):
    """VIF multicollinearity table (needs >=2 predictors; const stays in the design matrix
    for the formula). Shared by the linear and logistic diagnostics."""
    predictors = [c for c in x.columns if c != "const"]
    if len(predictors) < 2:
        return
    design = x.values
    vif_table = HTMLTableV2(table_caption=t("regression.diag.vif_caption"))
    header = [Cell(), Cell(t("regression.col.vif"), center=True)]
    if verbal:
        header.append(Cell(t("regression.diag.concern"), center=True))
    vif_table.add_title_row_apa(Row(header))

    high = []
    for i, name in enumerate(x.columns):
        if name == "const":
            continue
        vif = variance_inflation_factor(design, i)
        if not np.isnan(vif) and vif >= 10:
            high.append(str(name))
        cells = [Cell(str(name), push_to_left=True), Cell(format_statistic_apa(vif), center=True)]
        if verbal:
            cells.append(Cell(t(f"regression.vif.{_vif_key(vif)}"), center=True))
        vif_table.add_single_row_apa(Row(cells))
    prose and vif_table.add_text(
        t("regression.report.vif_high", items=smart_comma_join(high)) if high else t("regression.report.vif_ok")
    )
    result.update_and_add_element(vif_table, "regression vif")


def _mahalanobis(x: np.ndarray) -> np.ndarray:
    """Mahalanobis distance of each row from the predictor centroid (uses a pseudo-inverse so
    it survives collinear predictors)."""
    x = np.asarray(x, dtype=float)
    if x.ndim == 1:
        x = x.reshape(-1, 1)
    diff = x - x.mean(axis=0)
    cov = np.atleast_2d(np.cov(x, rowvar=False))
    inv = np.linalg.pinv(cov)
    md2 = np.einsum("ij,jk,ik->i", diff, inv, diff)
    return np.sqrt(np.clip(md2, 0.0, None))


def _add_influence_table(result, model, prose):
    """Influence diagnostics: per-observation Mahalanobis distance (multivariate outlyingness
    in predictor space), Cook's distance, leverage (hat) and internally studentized residuals,
    listing the observations that exceed the usual flags (Cook's D > 4/n, leverage > 2p/n,
    |std. resid| > 3, Mahalanobis D² > chi-square .999). Also reports the Durbin-Watson
    statistic for residual autocorrelation. All computed analytically, no resampling. This is
    a *report only* — nothing is excluded from the model."""
    influence = model.get_influence()
    cooks = np.asarray(influence.cooks_distance[0], dtype=float)
    leverage = np.asarray(influence.hat_matrix_diag, dtype=float)
    std_resid = np.asarray(influence.resid_studentized_internal, dtype=float)

    # Mahalanobis distance over the predictors only (drop the intercept column if present).
    exog = np.asarray(model.model.exog, dtype=float)
    predictors = exog[:, 1:] if exog.shape[1] > 1 else exog
    n_pred = predictors.shape[1]
    mahalanobis = _mahalanobis(predictors)
    maha_cut2 = float(stats.chi2.ppf(0.999, df=n_pred)) if n_pred else np.inf

    n = len(cooks)
    p = int(model.df_model) + 1  # predictors + intercept
    cooks_cut = 4.0 / n if n else np.nan
    leverage_cut = 2.0 * p / n if n else np.nan

    labels = list(model.fittedvalues.index)
    flagged = [
        i
        for i in range(n)
        if (cooks[i] > cooks_cut)
        or (leverage[i] > leverage_cut)
        or (abs(std_resid[i]) > 3)
        or (mahalanobis[i] ** 2 > maha_cut2)
    ]
    # Worst first, capped so the table stays readable.
    flagged.sort(key=lambda i: cooks[i], reverse=True)
    flagged = flagged[:20]

    table = HTMLTableV2(table_caption=t("regression.diag.influence_caption"))
    table.add_title_row_apa(
        Row(
            [
                Cell(t("regression.diag.observation")),
                Cell(t("regression.diag.mahalanobis"), center=True),
                Cell(t("regression.diag.cooks"), center=True),
                Cell(t("regression.diag.leverage"), center=True),
                Cell(t("regression.diag.std_resid"), center=True),
            ]
        )
    )
    for i in flagged:
        table.add_single_row_apa(
            Row(
                [
                    Cell(str(labels[i]), push_to_left=True),
                    Cell(format_statistic_apa(mahalanobis[i]), center=True),
                    Cell(format_statistic_apa(cooks[i]), center=True),
                    Cell(format_r_apa(leverage[i]), center=True),
                    Cell(format_statistic_apa(std_resid[i]), center=True),
                ]
            )
        )

    dw = float(durbin_watson(model.resid))
    if prose:
        if flagged:
            table.add_text(
                t(
                    "regression.report.influence_some",
                    n=len(flagged),
                    cooks=format_statistic_apa(cooks_cut),
                    leverage=format_r_apa(leverage_cut),
                )
            )
        else:
            table.add_text(t("regression.report.influence_none"))
        table.add_text(t("regression.report.durbin_watson", dw=format_statistic_apa(dw)))
    result.update_and_add_element(table, "regression influence")


def _add_diagnostics(result, model, x, verbal, prose):
    """OLS diagnostics: a VIF multicollinearity table (when there are >=2 predictors), an
    influence table (Cook's D / leverage / studentized residuals + Durbin-Watson), a
    residuals-vs-fitted plot, and a normal Q-Q plot of the residuals."""
    fitted = np.asarray(model.fittedvalues, dtype=float)
    resid = np.asarray(model.resid, dtype=float)

    _add_vif_table(result, x, verbal, prose)
    _add_influence_table(result, model, prose)

    # ----- Residuals vs fitted -----
    zero_x = np.array([fitted.min(), fitted.max()])
    result.update_and_add_element(
        PlotV2(
            items=[
                Scatter(x=fitted, y=resid, label=t("regression.diag.points")),
                Line(x=zero_x, y=np.array([0.0, 0.0]), label=t("regression.diag.zero")),
            ],
            title=t("regression.diag.resid_fitted"),
            plot_title=t("regression.diag.resid_fitted"),
            x_axis_title=t("regression.diag.fitted"),
            y_axis_title=t("regression.diag.residual"),
        ),
        "regression resid_fitted",
    )

    # ----- Normal Q-Q of residuals -----
    (osm, osr), (slope, intercept, _r) = stats.probplot(resid, dist="norm")
    line_x = np.array([osm.min(), osm.max()])
    result.update_and_add_element(
        PlotV2(
            items=[
                Scatter(x=osm, y=osr, label=t("regression.diag.points")),
                Line(x=line_x, y=intercept + slope * line_x, label=t("regression.diag.ref")),
            ],
            title=t("regression.diag.qq"),
            plot_title=t("regression.diag.qq"),
            x_axis_title=t("regression.diag.theoretical"),
            y_axis_title=t("regression.diag.sample"),
        ),
        "regression qq",
    )


def _coefficient_prose(model, dependent_column) -> str:
    """Explain what the coefficients mean and name the significant predictors (with the
    sign of their association)."""
    text = t("regression.report.coef_intro", dv=dependent_column)
    significant = []
    for param in model.params.index:
        if param == "const" or model.pvalues[param] >= 0.05:
            continue
        direction = t("regression.dir.positive") if model.params[param] >= 0 else t("regression.dir.negative")
        significant.append(f"{param} ({direction})")
    if significant:
        text += t("regression.report.coef_sig", dv=dependent_column, items=smart_comma_join(significant))
    else:
        text += t("regression.report.coef_none", dv=dependent_column)
    return text


@log_function
def recalculate_regression_study(elements, result: RegressionResult, update) -> RegressionResult:
    """Validate the inputs, fit an OLS model (with optional moderation / mediation), and
    build the fit, coefficient and (when relevant) path tables plus a plot. Unexpected
    exceptions are handled centrally by the panel's recalculate()."""
    cfg: RegressionStudyConfig = result.config
    result.result_elements = []

    cs = cfg.column_selector
    dependent_column = cs[0][0] if cs[0] else None
    independent_columns = list(cs[1]) if cs[1] else []
    moderator_column = cs[2][0] if cs[2] else None
    mediator_column = cs[3][0] if cs[3] else None

    if not dependent_column:
        return _fail(result, t("regression.error.no_dependent"))
    if not independent_columns:
        return _fail(result, t("regression.error.no_independent"))

    # Moderation and mediation are mutually exclusive: this module does not estimate a
    # moderated-mediation model, and combining them silently produces a misleading hybrid.
    if moderator_column and mediator_column:
        elements.column_selector.set_alert(2)
        elements.column_selector.set_alert(3)
        return _fail(result, t("regression.error.moderator_and_mediator"))

    all_columns = [dependent_column] + independent_columns
    if moderator_column is not None:
        all_columns.append(moderator_column)
    if mediator_column is not None:
        all_columns.append(mediator_column)
    if "const" in all_columns:
        return _fail(result, t("regression.error.const_reserved"))

    data = DATA_MANAGER.get_data_from_data_label(
        data_label=cfg.data_source,
        current_result_id=result.unique_id,
    )
    # Drop rows with any missing value in the used columns (list-wise) so OLS doesn't fail.
    df = data.get_dataframe(columns=all_columns, map_ordinal=True).dropna()
    update(10)

    verbal = bool(cfg.verbal_indicators)
    prose = prose_enabled(cfg.interpretation)
    show_std = bool(cfg.standardized)

    model_type = cfg.model_type or RegressionModelType.LINEAR.value
    if model_type == RegressionModelType.LOGISTIC.value:
        if mediator_column:
            elements.column_selector.set_alert(3)
            return _fail(result, t("regression.error.logit_no_mediation"))
        return _run_logistic(
            result, df, dependent_column, independent_columns, moderator_column, cfg, verbal, prose, update
        )
    if model_type == RegressionModelType.MULTINOMIAL.value:
        if mediator_column:
            elements.column_selector.set_alert(3)
            return _fail(result, t("regression.error.logit_no_mediation"))
        return _run_multinomial(
            result, df, dependent_column, independent_columns, moderator_column, cfg, verbal, prose, update
        )

    independent_cols = independent_columns.copy()
    if moderator_column:
        original_independent_cols = independent_cols.copy()
        independent_cols.append(moderator_column)
        for ind_col in original_independent_cols:
            interaction_term = f"{ind_col}&nbsp;*&nbsp;{moderator_column}"
            df[interaction_term] = df[ind_col] * df[moderator_column]
            independent_cols.append(interaction_term)

    mediator_model = None
    if mediator_column:
        x_mediator = sm.add_constant(df[independent_cols])
        mediator_model = sm.OLS(df[mediator_column], x_mediator).fit()
        independent_cols.append(mediator_column)

    n = len(df)
    if n < len(independent_cols) + 2:
        return _fail(result, t("regression.error.insufficient_data"))

    x = sm.add_constant(df[independent_cols])
    model = sm.OLS(df[dependent_column], x).fit()
    dependent_sd = df[dependent_column].std()
    update(45)

    # ----- Model fit table + verbal report -----
    fit_table = HTMLTableV2(table_caption=t("regression.caption.fit"))
    fit_header = [
        Cell(),
        Cell(t("regression.col.n"), center=True),
        Cell("R<sup>2</sup>", center=True),
        Cell(t("regression.col.adj_r2"), center=True),
        Cell(t("regression.col.f"), center=True),
        Cell("df", center=True),
        Cell(t("common.p_value"), center=True),
    ]
    if verbal:
        fit_header.append(Cell(t("verbal.col_significant"), center=True))
    fit_table.add_title_row_apa(Row(fit_header))

    fit_row = [
        Cell(t("regression.row.model"), push_to_left=True),
        Cell(str(n), center=True),
        Cell(format_r_apa(model.rsquared), center=True),
        Cell(format_r_apa(model.rsquared_adj), center=True),
        Cell(format_statistic_apa(model.fvalue), center=True),
        Cell(f"{int(model.df_model)}, {int(model.df_resid)}", center=True),
        Cell(format_p_apa_exact(model.f_pvalue), center=True),
    ]
    if verbal:
        fit_row.append(Cell(significance_verbal(model.f_pvalue), center=True))
    fit_table.add_single_row_apa(Row(fit_row))

    report = t(
        "regression.report.fit",
        pct=format_value_apa(model.rsquared * 100, 1),
        dv=dependent_column,
        r2=format_r_apa(model.rsquared),
        adj=format_r_apa(model.rsquared_adj),
        df1=int(model.df_model),
        df2=int(model.df_resid),
        f=format_statistic_apa(model.fvalue),
        p=format_p_apa_full(model.f_pvalue),
    )
    report += t("regression.report.significant") if model.f_pvalue < 0.05 else t("regression.report.not_significant")
    significant_predictors = [name for name in model.params.index if name != "const" and model.pvalues[name] < 0.05]
    report += (
        t("regression.report.predictors", items=smart_comma_join(significant_predictors))
        if significant_predictors
        else t("regression.report.predictors_none")
    )
    if prose:
        fit_table.add_text(report)
    result.update_and_add_element(fit_table, "regression fit")

    # ----- Coefficients table -----
    coefficients_table = _coefficient_table(
        model,
        dependent_sd,
        show_std,
        verbal,
        x,
        caption=t("regression.caption.coefficients"),
        intercept_label=t("regression.row.intercept"),
    )
    prose and coefficients_table.add_text(_coefficient_prose(model, dependent_column))
    result.update_and_add_element(coefficients_table, "regression coefficients")
    update(65)

    # ----- Path estimates table (mediation) -----
    if mediator_column:
        path_table = HTMLTableV2(table_caption=t("regression.caption.paths"))
        path_header = [
            Cell(),
            Cell(t("regression.col.b"), center=True),
            Cell(t("regression.col.se"), center=True),
            Cell(t("regression.col.t"), center=True),
            Cell(t("common.p_value"), center=True),
        ]
        if verbal:
            path_header.append(Cell(t("verbal.col_significant"), center=True))
        path_table.add_title_row_apa(Row(path_header))

        def _add_path_rows(path_model, target):
            for param in path_model.params.index:
                if param == "const":
                    continue
                p = path_model.pvalues[param]
                cells = [
                    Cell(f"{param}&nbsp;→&nbsp;{target}", push_to_left=True),
                    Cell(format_statistic_apa(path_model.params[param]), center=True),
                    Cell(format_statistic_apa(path_model.bse[param]), center=True),
                    Cell(format_statistic_apa(path_model.tvalues[param]), center=True),
                    Cell(format_p_apa_exact(p), center=True),
                ]
                if verbal:
                    cells.append(Cell(significance_verbal(p), center=True))
                path_table.add_single_row_apa(Row(cells))

        _add_path_rows(mediator_model, mediator_column)
        _add_path_rows(model, dependent_column)

        # Prose: the b path (mediator -> outcome) and each predictor's indirect effect a*b.
        b_path = model.params[mediator_column]
        indirect_items = [
            f"{param}: {_format_effect(mediator_model.params[param] * b_path)}"
            for param in independent_columns
            if param in mediator_model.params.index
        ]
        med_text = t("regression.report.med_intro", dv=dependent_column, mediator=mediator_column)
        med_text += t(
            "regression.report.med_b",
            mediator=mediator_column,
            dv=dependent_column,
            b=format_statistic_apa(b_path),
            p=format_p_apa_full(model.pvalues[mediator_column]),
        )
        if indirect_items:
            med_text += t("regression.report.med_indirect", items=smart_comma_join(indirect_items))
        prose and path_table.add_text(med_text)
        result.update_and_add_element(path_table, "regression paths")

        # Path diagram for the classic single-predictor X -> M -> Y mediation.
        if cfg.plots and len(independent_columns) == 1:
            iv = independent_columns[0]
            a = mediator_model.params.get(iv)
            b = model.params.get(mediator_column)
            c_direct = model.params.get(iv)
            if a is not None and b is not None and c_direct is not None:
                diagram = PlotV2(
                    items=[
                        MediationDiagram(
                            x_label=str(iv),
                            m_label=str(mediator_column),
                            y_label=str(dependent_column),
                            a=f"a = {format_statistic_apa(a)}",
                            b=f"b = {format_statistic_apa(b)}",
                            c_direct=f"c′ = {format_statistic_apa(c_direct)}",
                            indirect=f"a·b = {_format_effect(a * b)}",
                        )
                    ],
                    plot_title=t("regression.plot.mediation_title", dv=dependent_column),
                    x_axis_title="",
                    y_axis_title="",
                )
                result.update_and_add_element(diagram, "regression mediation diagram")

    # ----- Diagnostics (VIF + residual plots) -----
    if cfg.diagnostics:
        _add_diagnostics(result, model, x, verbal, prose)
    update(85)

    # ----- Plot (only for a single independent variable) -----
    if cfg.plots:
        plot_result_element = _build_plot(
            df, model, mediator_model, dependent_column, independent_columns, moderator_column, mediator_column
        )
        if plot_result_element is not None:
            result.update_and_add_element(plot_result_element, "regression plot")

    result.title_context = f"{str(dependent_column)[:16]} ~ " + ", ".join(str(c)[:16] for c in independent_columns)
    update(100)
    return result


def _build_observed_vs_predicted(df, model, dependent_column):
    """Multi-predictor fallback plot: observed outcome vs. the model's fitted values, with a
    45° reference line. Unlike the scatter+line plot it does not need a single predictor, so it is
    the meaningful 'plot' for a model with several predictors — points hugging the diagonal mean a
    good fit."""
    y = df[dependent_column].astype(float).values
    y_hat = np.asarray(model.fittedvalues, dtype=float)
    lo = float(min(y.min(), y_hat.min()))
    hi = float(max(y.max(), y_hat.max()))
    items = [
        Scatter(x=y_hat, y=y, label=t("regression.plot.data")),
        Line(x=np.array([lo, hi]), y=np.array([lo, hi]), label=t("regression.plot.identity")),
    ]
    title = t("regression.plot.obs_pred_title", dv=dependent_column)
    return PlotV2(
        items=items,
        title=title,
        plot_title=title,
        x_axis_title=t("regression.plot.predicted"),
        y_axis_title=t("regression.plot.observed"),
    )


def _build_plot(df, model, mediator_model, dependent_column, independent_columns, moderator_column, mediator_column):
    """Regression plot for a single predictor: scatter + fitted line, plus moderator simple
    slopes or mediation direct/total effects when those are in play. With several predictors there
    is no 2-D scatter, so an observed-vs-predicted plot is drawn instead."""
    if len(independent_columns) != 1:
        return _build_observed_vs_predicted(df, model, dependent_column)

    predictor = independent_columns[0]
    scatter = Scatter(x=df[predictor], y=df[dependent_column], label=t("regression.plot.data"))
    items = [scatter]

    x_grid = np.linspace(df[predictor].min(), df[predictor].max(), 100)
    x_values_original = pd.DataFrame({"const": 1, predictor: x_grid})

    if moderator_column:
        mean = df[moderator_column].mean()
        std = df[moderator_column].std()
        colors = Colors()
        for number_of_sds in [-1, 0, 1]:
            x_values = x_values_original.copy()
            x_values[moderator_column] = mean + number_of_sds * std
            x_values[f"{predictor}&nbsp;*&nbsp;{moderator_column}"] = x_values[predictor] * x_values[moderator_column]
            label = t("regression.plot.line_sd", sd=number_of_sds)
            items.append(
                Line(
                    x=x_values[predictor],
                    y=model.predict(x_values),
                    label=label,
                    legend_string=label,
                    config=LinePlotConfig(color=colors.get_color_list()),
                )
            )
    elif mediator_column:
        colors = Colors()
        xx = x_values_original[predictor]

        # Confidence band shared by the direct and total effect lines.
        conf_static = model.bse["const"]
        conf_direct = model.bse[predictor]
        conf_mediator_static = mediator_model.bse["const"]
        conf_mediator_dynamic = mediator_model.bse[predictor] * abs(xx - xx.mean())
        conf_mediator_total = np.sqrt(conf_mediator_static**2 + conf_mediator_dynamic**2)
        conf_indirect = np.sqrt(
            (conf_mediator_total**2) * (model.params[mediator_column] ** 2) + model.bse[mediator_column] ** 2
        )
        conf_interval = np.sqrt(conf_static**2 + conf_direct**2 + conf_indirect**2)

        # Direct effect (mediator held at its mean). Band first so the line sits on top.
        x_values = x_values_original.copy()
        x_values[mediator_column] = df[mediator_column].mean()
        yy = model.predict(sm.add_constant(x_values))
        color = colors.get_color_list()
        # Band labels must be unique across the plot (they key the settings panel), so they
        # carry the effect name rather than a shared "Standard error".
        items.append(
            Band(
                x=xx,
                y1=yy - conf_interval,
                y2=yy + conf_interval,
                label=t("regression.plot.direct"),
                config=BandPlotConfig(color=color),
            )
        )
        items.append(
            Line(
                x=xx,
                y=yy,
                label=t("regression.plot.direct"),
                legend_string=t("regression.plot.direct"),
                config=LinePlotConfig(color=color),
            )
        )

        # Total effect (mediator follows its own regression on the predictor).
        x_values = x_values_original.copy()
        x_values[mediator_column] = mediator_model.predict(sm.add_constant(x_values))
        yy = model.predict(sm.add_constant(x_values))
        color = colors.get_color_list()
        items.append(
            Band(
                x=xx,
                y1=yy - conf_interval,
                y2=yy + conf_interval,
                label=t("regression.plot.total"),
                config=BandPlotConfig(color=color),
            )
        )
        items.append(
            Line(
                x=xx,
                y=yy,
                label=t("regression.plot.total"),
                legend_string=t("regression.plot.total"),
                config=LinePlotConfig(color=color),
            )
        )
    else:
        items.append(
            Line(
                x=x_values_original[predictor],
                y=model.predict(sm.add_constant(x_values_original)),
                label=t("regression.plot.line"),
            )
        )

    title = t("regression.plot.title", dv=dependent_column, iv=predictor)
    return PlotV2(
        items=items,
        title=title,
        plot_title=title,
        x_axis_title=predictor,
        y_axis_title=dependent_column,
    )


# ===================================================================================
#  Logistic regression (binary outcome)
# ===================================================================================


def _run_logistic(result, df, dependent_column, independent_columns, moderator_column, cfg, verbal, prose, update):
    """Fit a binary logistic regression (statsmodels Logit) and build the fit, coefficient
    and (optional) diagnostics/plot. Moderation is supported via interaction terms;
    mediation is not (filtered out by the caller)."""
    # ----- Moderation: add the moderator and its product with each predictor -----
    independent_cols = independent_columns.copy()
    if moderator_column:
        original_independent_cols = independent_cols.copy()
        independent_cols.append(moderator_column)
        for ind_col in original_independent_cols:
            interaction_term = f"{ind_col}&nbsp;*&nbsp;{moderator_column}"
            df[interaction_term] = df[ind_col] * df[moderator_column]
            independent_cols.append(interaction_term)

    # ----- Binary outcome: map the two distinct values to 0/1 (positive = the larger one) -----
    distinct = sorted(pd.unique(df[dependent_column]))
    if len(distinct) != 2:
        return _fail(result, t("regression.error.not_binary", values=len(distinct)))
    positive_label = distinct[1]
    y = df[dependent_column].map({distinct[0]: 0, distinct[1]: 1})

    n = len(df)
    if n < len(independent_cols) + 2:
        return _fail(result, t("regression.error.insufficient_data"))

    x = sm.add_constant(df[independent_cols])
    model = sm.Logit(y, x).fit(disp=0)
    update(45)

    # ----- Model fit table (pseudo-R², likelihood-ratio test) -----
    fit_table = HTMLTableV2(table_caption=t("regression.caption.fit"))
    fit_header = [
        Cell(),
        Cell(t("regression.col.n"), center=True),
        Cell(t("regression.col.pseudo_r2"), center=True),
        Cell("χ²", center=True),
        Cell("df", center=True),
        Cell(t("common.p_value"), center=True),
    ]
    if verbal:
        fit_header.append(Cell(t("verbal.col_significant"), center=True))
    fit_table.add_title_row_apa(Row(fit_header))

    fit_row = [
        Cell(t("regression.row.model"), push_to_left=True),
        Cell(str(n), center=True),
        Cell(format_r_apa(model.prsquared), center=True),
        Cell(format_statistic_apa(model.llr), center=True),
        Cell(str(int(model.df_model)), center=True),
        Cell(format_p_apa_exact(model.llr_pvalue), center=True),
    ]
    if verbal:
        fit_row.append(Cell(significance_verbal(model.llr_pvalue), center=True))
    fit_table.add_single_row_apa(Row(fit_row))

    report = t(
        "regression.report.logit_fit",
        dv=dependent_column,
        positive=positive_label,
        pseudo=format_r_apa(model.prsquared),
        chi2=format_statistic_apa(model.llr),
        df=int(model.df_model),
        p=format_p_apa_full(model.llr_pvalue),
    )
    report += t("regression.report.significant") if model.llr_pvalue < 0.05 else t("regression.report.not_significant")
    if prose:
        fit_table.add_text(report)
    result.update_and_add_element(fit_table, "regression fit")

    # ----- Coefficients table (log-odds B, SE, odds ratio, z, p) -----
    coefficients_table = HTMLTableV2(table_caption=t("regression.caption.coefficients"))
    header = [
        Cell(),
        Cell(t("regression.col.b"), center=True),
        Cell(t("regression.col.se"), center=True),
        Cell(t("regression.col.odds_ratio"), center=True),
        Cell(t("regression.col.z"), center=True),
        Cell(t("common.p_value"), center=True),
    ]
    if verbal:
        header.append(Cell(t("verbal.col_significant"), center=True))
    coefficients_table.add_title_row_apa(Row(header))

    for param in model.params.index:
        p = model.pvalues[param]
        name = t("regression.row.intercept") if param == "const" else param
        cells = [
            Cell(name, push_to_left=True),
            Cell(format_statistic_apa(model.params[param]), center=True),
            Cell(format_statistic_apa(model.bse[param]), center=True),
            Cell(format_statistic_apa(np.exp(model.params[param])), center=True),
            Cell(format_statistic_apa(model.tvalues[param]), center=True),
            Cell(format_p_apa_exact(p), center=True),
        ]
        if verbal:
            cells.append(Cell(significance_verbal(p), center=True))
        coefficients_table.add_single_row_apa(Row(cells))

    prose and coefficients_table.add_text(_logistic_coefficient_prose(model, dependent_column, positive_label))
    result.update_and_add_element(coefficients_table, "regression coefficients")
    update(70)

    # ----- Diagnostics (VIF only; the OLS residual plots don't transfer to logistic) -----
    if cfg.diagnostics:
        _add_vif_table(result, x, verbal, prose)

    # ----- Plot (single predictor: fitted probability curve over the observed 0/1 outcome) -----
    if cfg.plots:
        plot_element = _build_logistic_plot(
            df, model, y, dependent_column, independent_columns, moderator_column, positive_label
        )
        if plot_element is not None:
            result.update_and_add_element(plot_element, "regression plot")

    result.title_context = f"{str(dependent_column)[:16]} ~ " + ", ".join(str(c)[:16] for c in independent_columns)
    update(100)
    return result


def _logistic_coefficient_prose(model, dependent_column, positive_label) -> str:
    """Name the significant predictors and whether they raise or lower the odds of the
    positive outcome."""
    text = t("regression.report.logit_coef_intro", dv=dependent_column, positive=positive_label)
    significant = []
    for param in model.params.index:
        if param == "const" or model.pvalues[param] >= 0.05:
            continue
        direction = t("regression.dir.increase") if model.params[param] >= 0 else t("regression.dir.decrease")
        significant.append(f"{param} ({direction})")
    if significant:
        text += t("regression.report.logit_coef_sig", positive=positive_label, items=smart_comma_join(significant))
    else:
        text += t("regression.report.coef_none", dv=dependent_column)
    return text


# ===================================================================================
#  Multinomial logistic regression (3+ unordered outcome categories)
# ===================================================================================


def _run_multinomial(result, df, dependent_column, independent_columns, moderator_column, cfg, verbal, prose, update):
    """Fit a multinomial logistic regression (statsmodels MNLogit) for an unordered outcome
    with 3+ categories. Coefficients are reported as a block per non-reference category (vs the
    first category as the baseline). Moderation is supported via interaction terms; mediation
    is not (filtered out by the caller)."""
    independent_cols = independent_columns.copy()
    if moderator_column:
        original_independent_cols = independent_cols.copy()
        independent_cols.append(moderator_column)
        for ind_col in original_independent_cols:
            interaction_term = f"{ind_col}&nbsp;*&nbsp;{moderator_column}"
            df[interaction_term] = df[ind_col] * df[moderator_column]
            independent_cols.append(interaction_term)

    # Encode the outcome to 0..K-1; the first category (code 0) is the reference/baseline.
    codes, categories = pd.factorize(df[dependent_column], sort=True)
    categories = list(categories)
    if len(categories) < 3:
        return _fail(result, t("regression.error.not_multinomial", values=len(categories)))

    n = len(df)
    if n < len(independent_cols) + 2:
        return _fail(result, t("regression.error.insufficient_data"))

    x = sm.add_constant(df[independent_cols])
    model = sm.MNLogit(codes, x).fit(disp=0)
    base = categories[0]
    update(45)

    # ----- Model fit table (pseudo-R², likelihood-ratio test) -----
    fit_table = HTMLTableV2(table_caption=t("regression.caption.fit"))
    fit_header = [
        Cell(),
        Cell(t("regression.col.n"), center=True),
        Cell(t("regression.col.pseudo_r2"), center=True),
        Cell("χ²", center=True),
        Cell("df", center=True),
        Cell(t("common.p_value"), center=True),
    ]
    if verbal:
        fit_header.append(Cell(t("verbal.col_significant"), center=True))
    fit_table.add_title_row_apa(Row(fit_header))

    fit_row = [
        Cell(t("regression.row.model"), push_to_left=True),
        Cell(str(n), center=True),
        Cell(format_r_apa(model.prsquared), center=True),
        Cell(format_statistic_apa(model.llr), center=True),
        Cell(str(int(model.df_model)), center=True),
        Cell(format_p_apa_exact(model.llr_pvalue), center=True),
    ]
    if verbal:
        fit_row.append(Cell(significance_verbal(model.llr_pvalue), center=True))
    fit_table.add_single_row_apa(Row(fit_row))

    report = t(
        "regression.report.multinom_fit",
        dv=dependent_column,
        base=base,
        pseudo=format_r_apa(model.prsquared),
        chi2=format_statistic_apa(model.llr),
        df=int(model.df_model),
        p=format_p_apa_full(model.llr_pvalue),
    )
    report += t("regression.report.significant") if model.llr_pvalue < 0.05 else t("regression.report.not_significant")
    if prose:
        fit_table.add_text(report)
    result.update_and_add_element(fit_table, "regression fit")

    # ----- Coefficients: one block per non-reference category (log-odds B, SE, OR, z, p) -----
    coefficients_table = HTMLTableV2(table_caption=t("regression.caption.coefficients"))
    n_cols = 7 if verbal else 6
    header = [
        Cell(),
        Cell(t("regression.col.b"), center=True),
        Cell(t("regression.col.se"), center=True),
        Cell(t("regression.col.odds_ratio"), center=True),
        Cell(t("regression.col.z"), center=True),
        Cell(t("common.p_value"), center=True),
    ]
    if verbal:
        header.append(Cell(t("verbal.col_significant"), center=True))
    coefficients_table.add_title_row_apa(Row(header))

    param_index = list(model.params.index)
    for col in range(model.params.shape[1]):
        params_col = model.params.iloc[:, col]
        bse_col = model.bse.iloc[:, col]
        tv_col = model.tvalues.iloc[:, col]
        pv_col = model.pvalues.iloc[:, col]
        coefficients_table.add_single_row_apa(
            Row(
                [
                    Cell(
                        t("regression.multinom.vs_base", cat=categories[col + 1], base=base),
                        col_span=n_cols,
                        is_bold=True,
                        push_to_left=True,
                        border_bottom=True,
                    )
                ]
            )
        )
        for param in param_index:
            pv = pv_col.loc[param]
            name = t("regression.row.intercept") if param == "const" else param
            cells = [
                Cell(name, push_to_left=True),
                Cell(format_statistic_apa(params_col.loc[param]), center=True),
                Cell(format_statistic_apa(bse_col.loc[param]), center=True),
                Cell(format_statistic_apa(np.exp(params_col.loc[param])), center=True),
                Cell(format_statistic_apa(tv_col.loc[param]), center=True),
                Cell(format_p_apa_exact(pv), center=True),
            ]
            if verbal:
                cells.append(Cell(significance_verbal(pv), center=True))
            coefficients_table.add_single_row_apa(Row(cells))

    prose and coefficients_table.add_text(_multinomial_coefficient_prose(model, dependent_column, categories))
    result.update_and_add_element(coefficients_table, "regression coefficients")
    update(70)

    # ----- Diagnostics (VIF only; the OLS residual plots don't transfer to logistic) -----
    if cfg.diagnostics:
        _add_vif_table(result, x, verbal, prose)

    result.title_context = f"{str(dependent_column)[:16]} ~ " + ", ".join(str(c)[:16] for c in independent_columns)
    update(100)
    return result


def _multinomial_coefficient_prose(model, dependent_column, categories) -> str:
    """For each non-reference category, name the predictors that significantly shift its odds
    relative to the baseline."""
    base = categories[0]
    text = t("regression.report.multinom_intro", dv=dependent_column, base=base)
    param_index = list(model.params.index)
    parts = []
    for col in range(model.params.shape[1]):
        params_col = model.params.iloc[:, col]
        pv_col = model.pvalues.iloc[:, col]
        significant = []
        for param in param_index:
            if param == "const" or pv_col.loc[param] >= 0.05:
                continue
            direction = t("regression.dir.increase") if params_col.loc[param] >= 0 else t("regression.dir.decrease")
            significant.append(f"{param} ({direction})")
        if significant:
            parts.append(
                t(
                    "regression.report.multinom_cat",
                    cat=categories[col + 1],
                    base=base,
                    items=smart_comma_join(significant),
                )
            )
    text += " " + " ".join(parts) if parts else t("regression.report.coef_none", dv=dependent_column)
    return text


def _build_logistic_plot(df, model, y, dependent_column, independent_columns, moderator_column, positive_label):
    """Logistic plot for a single predictor: the observed 0/1 outcome as points plus the
    fitted probability curve (simple slopes at ±1 SD of the moderator when present)."""
    if len(independent_columns) != 1:
        return None

    predictor = independent_columns[0]
    items = [Scatter(x=df[predictor], y=y, label=t("regression.plot.data"))]

    x_grid = np.linspace(df[predictor].min(), df[predictor].max(), 100)
    x_values_original = pd.DataFrame({"const": 1, predictor: x_grid})

    if moderator_column:
        mean = df[moderator_column].mean()
        std = df[moderator_column].std()
        colors = Colors()
        for number_of_sds in [-1, 0, 1]:
            x_values = x_values_original.copy()
            x_values[moderator_column] = mean + number_of_sds * std
            x_values[f"{predictor}&nbsp;*&nbsp;{moderator_column}"] = x_values[predictor] * x_values[moderator_column]
            label = t("regression.plot.line_sd", sd=number_of_sds)
            items.append(
                Line(
                    x=x_values[predictor],
                    y=model.predict(x_values),
                    label=label,
                    legend_string=label,
                    config=LinePlotConfig(color=colors.get_color_list()),
                )
            )
    else:
        items.append(
            Line(
                x=x_grid,
                y=model.predict(x_values_original),
                label=t("regression.plot.prob_curve"),
            )
        )

    title = t("regression.plot.logit_title", dv=dependent_column, iv=predictor, positive=positive_label)
    return PlotV2(
        items=items,
        title=title,
        plot_title=title,
        x_axis_title=predictor,
        y_axis_title=t("regression.plot.prob_axis", positive=positive_label),
    )
