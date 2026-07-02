# Confirmatory factor analysis

**Confirmatory Factor Analysis (CFA)** tests how well a **pre-specified** factor structure
fits the data, reporting standard fit indices. Use CFA when you already have a hypothesised
measurement model — for example, from prior theory or an {doc}`exploratory-factor-analysis`.

## When to use it

When you can state in advance which items load on which factor and want to judge how well
that model fits.

## Inputs

- **Variables** — the numeric/ordinal items that make up your hypothesised factors.
- **Model** — which items load on which factor.

## Options

- **Estimator** — **Maximum Likelihood (ML)** or **Diagonally Weighted Least Squares (DWLS)**
  (DWLS suits ordinal items).
- **Allow factor correlation** — oblique (correlated factors) vs orthogonal.
- **Modification hints** — adds a table of possible cross-loadings, ranked by the mean absolute
  standardized residual between an item and another factor's indicators. These are
  residual-based *hints*, not exact Lagrange-multiplier modification indices.
- **Apply cross-loadings** — a checklist of the current suggestions (and any already applied).
  Tick one to add that item as a cross-loading on the suggested factor; the model re-fits with
  it, and the loadings table then shows the item loading on both factors. Untick to revert.

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
  The overall figure honours the shared **Plot Size** slider.

## Notes

- You need enough complete cases for a stable solution, and the model must be identified
  (each factor needs enough indicators).
