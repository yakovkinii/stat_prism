# Confirmatory factor analysis

**Confirmatory Factor Analysis (CFA)** tests how well a **pre-specified** factor structure
fits the data, reporting standard fit indices. Use CFA when you already have a hypothesized
measurement model — for example, from prior theory or an {doc}`exploratory-factor-analysis`.

## When to use it

When you can state in advance which items load on which factor and want to judge how well
that model fits.

## Inputs

- **Variables** — the numeric/ordinal items that make up your hypothesized factors.
- **Model** — which items load on which factor.

## Options

- **Estimator** — **Maximum Likelihood (ML)** or **Diagonally Weighted Least Squares (DWLS)**
  (DWLS suits ordinal items).
- **Allow factor correlation** — oblique (correlated factors) vs orthogonal.
- **Second-order factor** — adds a general factor that explains the correlations among the
  first-order factors (needs at least 3 first-order factors). With exactly three, the
  second-order part is just-identified, so its fit matches the oblique model; it differs only
  with four or more factors.
- **Modification hints (cross-loadings)** — a table of possible cross-loadings, ranked by the
  mean absolute standardized residual between an item and another factor's indicators.
- **Modification hints (correlated residuals)** — a table of item pairs whose residuals covary
  most (candidates for letting two items' measurement errors correlate — e.g. similar wording,
  content, method, or reverse scoring). Both tables are residual-based *hints*, not exact
  Lagrange-multiplier modification indices.
- **Apply cross-loadings** — a checklist of the current cross-loading suggestions (and any
  already applied). Tick one to add that item as a cross-loading on the suggested factor; the
  model re-fits, and the loadings table then shows the item loading on both factors. Untick to
  revert.
- **Apply correlated residuals** — the same idea for residual covariances: tick an item pair to
  free the covariance between their residuals and re-fit. Untick to revert.
- **Create a Calculate Scale step per factor** (button at the bottom) — for each factor, adds a
  new {doc}`../data-processing/calculate-scale` step with that factor's items pre-selected. The
  scale name is left blank on purpose, so each new step prompts you to name it. Pressing the
  button always adds fresh steps.

## Output

- **Fit indices** — the standard measures used to judge how well the model reproduces the
  observed relationships.
- **Factor loadings** for the specified structure.
- With **Plots** on, a loadings **heatmap** and a **factor-structure path diagram** — factors
  right-aligned on the left, indicators left-aligned on the right, linked by their standardized
  loadings (factor correlations shown as links for oblique models). Its plot settings offer
  **Vertical spacing** and **Horizontal distance** sliders (which set the boxes' separation
  without changing their size), an **Arrow color** picker, an **Arrow label size** slider (the
  loading numbers), a **Correlation curve** slider (0 = straight, up to a full bulge for the
  factor-correlation links), and an **Arrow width ∝ loading** toggle (uniform arrows otherwise).
  The overall figure honors the shared **Plot Size** slider.

## Notes

- You need enough complete cases for a stable solution, and the model must be identified
  (each factor needs enough indicators).
- With the **DWLS** estimator the fit indices (χ², RMSEA, CFI, TLI) are the robust,
  mean-and-variance-adjusted (Satorra–Bentler / WLSMV) versions, so the degrees of freedom can
  be fractional.
