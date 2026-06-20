#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import logging
import math

import numpy as np
from scipy.stats import norm
from statsmodels.stats.power import FTestAnovaPower, TTestIndPower, TTestPower

from src.common.decorators import log_function
from src.common.qcolor import Colors
from src.side_area_panel.modules.common.result.html_result import Cell, HTMLTableV2, Row
from src.side_area_panel.modules.common.result.plot_result import (
    Line,
    LinePlotConfig,
    PlotV2,
    Scatter,
)
from src.side_area_panel.modules.common.utility import format_value_apa
from src.side_area_panel.modules.power_analysis.power_analysis_result import (
    EFFECT_SYMBOL,
    SOLVE_FOR,
    TAILS,
    TEST_TYPES,
    PowerAnalysisResult,
)


def _fail(result: PowerAnalysisResult, message: str) -> PowerAnalysisResult:
    """Show a validation message to the user and log it, then stop."""
    logging.warning("Power analysis: %s", message)
    result.set_error(message)
    return result


def _parse_float(text):
    try:
        return float(str(text).strip())
    except (TypeError, ValueError):
        return None


def _parse_pos(text):
    value = _parse_float(text)
    return value if value is not None and value > 0 else None


# ----- Per-test power engines -----------------------------------------------------------
# Each engine exposes power(effect, n, alpha), nobs(effect, alpha, power) and
# effect(n, alpha, power); `n` is per-group for the t-tests/correlation and total N for ANOVA.


def _z_alpha(alpha, two_sided):
    return norm.ppf(1 - alpha / 2) if two_sided else norm.ppf(1 - alpha)


def _corr_power(effect, n, alpha, two_sided):
    if n <= 3:
        return np.nan
    zr = np.arctanh(min(abs(effect), 0.999))
    return float(norm.cdf(zr * np.sqrt(n - 3) - _z_alpha(alpha, two_sided)))


def _corr_nobs(effect, alpha, power, two_sided):
    zr = np.arctanh(min(abs(effect), 0.999))
    if zr == 0:
        return np.nan
    return ((_z_alpha(alpha, two_sided) + norm.ppf(power)) / zr) ** 2 + 3


def _corr_effect(n, alpha, power, two_sided):
    if n <= 3:
        return np.nan
    return float(np.tanh((_z_alpha(alpha, two_sided) + norm.ppf(power)) / np.sqrt(n - 3)))


@log_function
def recalculate_power_analysis_study(elements, result: PowerAnalysisResult, update) -> PowerAnalysisResult:
    """Solve for sample size, power, or effect size for the chosen test, given the other
    three quantities. Builds a results table and a power-vs-sample-size curve. Unexpected
    exceptions are handled centrally by the panel's recalculate()."""
    cfg = result.config
    result.result_elements = []

    test = cfg.test_type or TEST_TYPES[0]
    solve_for = cfg.solve_for or SOLVE_FOR[0]
    two_sided = (cfg.tails or TAILS[0]) == TAILS[0]
    alt = "two-sided" if two_sided else "larger"
    is_anova = test == "One-way ANOVA"
    is_corr = test == "Correlation"
    symbol = EFFECT_SYMBOL[test]

    alpha = _parse_pos(cfg.alpha)
    if alpha is None or alpha >= 1:
        return _fail(result, "Alpha must be a number between 0 and 1 (e.g. 0.05).")

    power = _parse_pos(cfg.power)
    effect = _parse_float(cfg.effect_size)
    n = _parse_pos(cfg.sample_size)

    k = None
    if is_anova:
        k_val = _parse_pos(cfg.n_groups)
        k = int(round(k_val)) if k_val is not None else None
        if k is None or k < 2:
            return _fail(result, "Number of groups must be an integer ≥ 2 for ANOVA.")

    update(20)

    # --- Solve for the requested quantity ---------------------------------------------
    solved_label = ""
    solved_value = None
    n_per_group = None
    n_total = None
    try:
        if solve_for == "Sample size":
            if power is None or power >= 1:
                return _fail(result, "Power must be a number between 0 and 1 (e.g. 0.80).")
            if effect is None or effect == 0:
                return _fail(result, "Effect size must be a non-zero number.")
            if is_corr:
                raw = _corr_nobs(effect, alpha, power, two_sided)
            elif is_anova:
                raw = FTestAnovaPower().solve_power(effect_size=abs(effect), nobs=None, alpha=alpha, power=power, k_groups=k)
            elif test == "Two-sample t-test":
                raw = TTestIndPower().solve_power(effect_size=abs(effect), nobs1=None, alpha=alpha, power=power, ratio=1.0, alternative=alt)
            else:
                raw = TTestPower().solve_power(effect_size=abs(effect), nobs=None, alpha=alpha, power=power, alternative=alt)
            if raw is None or not np.isfinite(raw):
                return _fail(result, "Could not solve for sample size with these inputs.")
            if is_anova:
                n_total = int(math.ceil(raw))
                n_per_group = int(math.ceil(raw / k))
                solved_value, solved_label = n_total, "Required total N"
            else:
                n_per_group = int(math.ceil(raw))
                n_total = n_per_group * (2 if test == "Two-sample t-test" else 1)
                solved_value, solved_label = n_per_group, "Required n per group"

        elif solve_for == "Power":
            if effect is None or effect == 0:
                return _fail(result, "Effect size must be a non-zero number.")
            if n is None:
                return _fail(result, "Sample size must be a positive number.")
            if is_corr:
                solved_value = _corr_power(effect, n, alpha, two_sided)
            elif is_anova:
                solved_value = FTestAnovaPower().power(effect_size=abs(effect), nobs=n, alpha=alpha, k_groups=k)
            elif test == "Two-sample t-test":
                solved_value = TTestIndPower().power(effect_size=abs(effect), nobs1=n, alpha=alpha, ratio=1.0, alternative=alt)
            else:
                solved_value = TTestPower().power(effect_size=abs(effect), nobs=n, alpha=alpha, alternative=alt)
            solved_label = "Achieved power"
            power = solved_value

        else:  # Effect size
            if power is None or power >= 1:
                return _fail(result, "Power must be a number between 0 and 1 (e.g. 0.80).")
            if n is None:
                return _fail(result, "Sample size must be a positive number.")
            if is_corr:
                solved_value = _corr_effect(n, alpha, power, two_sided)
            elif is_anova:
                solved_value = FTestAnovaPower().solve_power(effect_size=None, nobs=n, alpha=alpha, power=power, k_groups=k)
            elif test == "Two-sample t-test":
                solved_value = TTestIndPower().solve_power(effect_size=None, nobs1=n, alpha=alpha, power=power, ratio=1.0, alternative=alt)
            else:
                solved_value = TTestPower().solve_power(effect_size=None, nobs=n, alpha=alpha, power=power, alternative=alt)
            solved_label = f"Minimum detectable effect size ({symbol})"
            effect = solved_value
    except Exception as e:  # statsmodels raises on impossible parameter combos
        return _fail(result, f"Could not solve with these inputs: {e}")

    if solved_value is None or not np.isfinite(solved_value):
        return _fail(result, "Could not solve with these inputs.")

    update(60)

    # Resolve the n actually used for display / the curve.
    if solve_for == "Sample size":
        display_n = n_total if is_anova else n_per_group
    else:
        display_n = n
        if is_anova:
            n_total = n
            n_per_group = n / k

    # --- Results table -----------------------------------------------------------------
    table = HTMLTableV2(table_caption=f"Power analysis — {test}")
    table.add_title_row_apa(Row([Cell("Quantity"), Cell("Value", center=True)]))

    def _row(name, value, highlight=False):
        label = Cell(name, push_to_left=True)
        val = Cell(value, center=True)
        table.add_single_row_apa(Row([label, val]))

    _row("Test", test)
    _row("Solve for", solve_for)
    if not is_anova:
        _row("Tails", cfg.tails or TAILS[0])
    _row("Alpha (α)", format_value_apa(alpha, 3))
    _row("Power (1 − β)", format_value_apa(power, 3) if power is not None else "—")
    _row(f"Effect size ({symbol})", format_value_apa(effect, 3) if effect is not None else "—")
    if is_anova:
        _row("Number of groups", str(k))
        _row("Total N", str(int(math.ceil(n_total))) if n_total is not None else "—")
        _row("n per group", str(int(math.ceil(n_per_group))) if n_per_group is not None else "—")
    else:
        _row("n per group", str(int(math.ceil(display_n))) if display_n is not None else "—")

    # Solved-value highlight row (as prose, so it stands out regardless of theme).
    if solve_for == "Effect size":
        solved_text = f"{solved_label}: {symbol} = {format_value_apa(solved_value, 3)}"
    elif solve_for == "Power":
        solved_text = f"{solved_label}: {format_value_apa(solved_value, 3)}"
    else:
        solved_text = f"{solved_label}: {int(solved_value)}"
    table.add_text(
        f"<b>{solved_text}.</b> "
        + _interpretation(test, solve_for, solved_value, symbol)
    )
    result.update_and_add_element(table, "power table")
    update(75)

    # --- Power-vs-sample-size curve ----------------------------------------------------
    curve = _power_curve(test, effect, alpha, two_sided, k, display_n, power, is_anova, is_corr, alt, symbol)
    if curve is not None:
        result.update_and_add_element(curve, "power curve")

    result.title_context = f"{test} — {solve_for}"
    update(100)
    return result


def _interpretation(test, solve_for, value, symbol) -> str:
    if solve_for == "Sample size":
        return "This is the smallest sample that reaches the requested power at the given effect size and α."
    if solve_for == "Power":
        if value >= 0.8:
            return "The study is adequately powered (≥ .80) to detect this effect."
        return "The study is underpowered (< .80): consider a larger sample or a larger expected effect."
    return f"Effects smaller than {symbol} = {format_value_apa(value, 3)} are unlikely to be detected at this sample size and power."


def _power_curve(test, effect, alpha, two_sided, k, solved_n, target_power, is_anova, is_corr, alt, symbol):
    """Power as a function of sample size at the resolved effect size, with a horizontal
    target-power line and a marker at the resolved n."""
    if effect is None or effect == 0 or solved_n is None or not np.isfinite(solved_n):
        return None

    upper = max(int(solved_n * 2), 40)
    lower = max(4, int(solved_n * 0.1)) if is_corr else 2
    xs = np.unique(np.linspace(lower, upper, 60).astype(int))
    xs = xs[xs > (3 if is_corr else 1)]
    if len(xs) < 2:
        return None

    def power_at(n):
        try:
            if is_corr:
                return _corr_power(effect, n, alpha, two_sided)
            if is_anova:
                return FTestAnovaPower().power(effect_size=abs(effect), nobs=n, alpha=alpha, k_groups=k)
            if test == "Two-sample t-test":
                return TTestIndPower().power(effect_size=abs(effect), nobs1=n, alpha=alpha, ratio=1.0, alternative=alt)
            return TTestPower().power(effect_size=abs(effect), nobs=n, alpha=alpha, alternative=alt)
        except Exception:
            return np.nan

    ys = np.array([power_at(n) for n in xs], dtype=float)

    colors = Colors()
    x_axis = "Total N" if is_anova else "n per group"
    items = [
        Line(
            x=xs.astype(float), y=ys, label="Power",
            legend_string="Power", config=LinePlotConfig(color=colors.get_color_list()),
        ),
        Scatter(x=xs.astype(float), y=ys, label="Power"),
    ]
    if target_power is not None and np.isfinite(target_power):
        items.append(
            Line(
                x=np.array([float(xs.min()), float(xs.max())]),
                y=np.array([float(target_power), float(target_power)]),
                label=f"Target power ({format_value_apa(target_power, 2)})",
                legend_string=f"Target power ({format_value_apa(target_power, 2)})",
                config=LinePlotConfig(color=colors.get_color_list()),
            )
        )

    title = f"Power vs sample size ({symbol} = {format_value_apa(effect, 2)})"
    return PlotV2(
        items=items,
        title=title,
        plot_title=title,
        x_axis_title=x_axis,
        y_axis_title="Power (1 − β)",
    )
