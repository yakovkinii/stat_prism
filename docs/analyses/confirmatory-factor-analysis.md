# Confirmatory factor analysis

**Confirmatory Factor Analysis (CFA)** tests how well a **pre-specified** factor structure
fits the data, reporting standard fit indices. Use CFA when you already have a hypothesized
measurement model, for example from prior theory or an {doc}`exploratory-factor-analysis`.

## When to use it

When you can state in advance which items load on which factor and want to judge how well
that model fits.

## Inputs

- **Variables**: the numeric/ordinal items that make up your hypothesized factors.
- **Model**: which items load on which factor.

## Options

- **Estimator**: one of three:
  - **Maximum Likelihood (ML)**: the default for continuous (interval/ratio) items.
  - **Diagonally Weighted Least Squares (DWLS)**: a robust least-squares estimator for
    non-normal continuous items. ML and DWLS both treat the items *numerically*: ordinal items
    are used via their numeric face values (you get a warning that they were cast, and an error if
    a category is not a number).
  - **Unweighted LS (polychoric)**: the ordinal estimator. It works on the polychoric correlation
    matrix of the ordinal order codes (tetrachoric for binary items), so it is the one to choose
    when your items are genuinely ordinal Likert responses rather than interval scores.
- **Allow factor correlation**: oblique (correlated factors) vs orthogonal.
- **Second-order factor**: adds a general factor that explains the correlations among the
  first-order factors (needs at least 3 first-order factors). With exactly three, the
  second-order part is just-identified, so its fit matches the oblique model; it differs only
  with four or more factors.
- **Modification hints (cross-loadings)**: a table of possible cross-loadings, ranked by the
  mean absolute standardized residual between an item and another factor's indicators.
- **Modification hints (correlated residuals)**: a table of item pairs whose residuals covary
  most (candidates for letting two items' measurement errors correlate: e.g. similar wording,
  content, method, or reverse scoring). Both tables are residual-based *hints*, not exact
  Lagrange-multiplier modification indices.
- **Apply cross-loadings**: a checklist of the current cross-loading suggestions (and any
  already applied). Only the **top 6** suggestions are listed, with the total count shown in the
  heading (e.g. *Apply cross-loadings (54)*). Tick one to add that item as a cross-loading on the
  suggested factor; the model re-fits, and the loadings table then shows the item loading on both
  factors. Untick to revert.
- **Apply correlated residuals**: the same idea for residual covariances (top 6 shown, total in
  the heading): tick an item pair to free the covariance between their residuals and re-fit. Untick
  to revert.
- **Create a Calculate Scale step per factor** (button at the bottom): for each factor, adds a
  new {doc}`../data-processing/calculate-scale` step with that factor's items pre-selected. The
  scale name is left blank on purpose, so each new step prompts you to name it. Pressing the
  button always adds fresh steps.

## Output

- **Fit indices**: the standard measures used to judge how well the model reproduces the
  observed relationships.
- **Factor loadings** for the specified structure.
- With **Plots** on, a loadings **heatmap** and a **factor-structure path diagram**: factors
  right-aligned on the left, indicators left-aligned on the right, linked by their standardized
  loadings (factor correlations shown as links for oblique models). Any **applied cross-loadings**
  are drawn as dashed arrows to the second factor, and **freed residual correlations** as curved
  links between the two indicators, so the diagram reflects the full fitted model. The figure size
  is set by the shared **Plot Size** (width) and **Aspect** sliders; the **Vertical spacing** and
  **Horizontal distance** sliders then distribute the boxes *within* that fixed size. The diagram
  also has its own controls:
  - **Arrow color**: the color of the arrows and links.
  - **Arrow label size**: the loading numbers.
  - **Name label size**: the factor and indicator names (they start smaller and shrink further
    for larger models).
  - **Correlation curve**: 0 is straight, rising to a full bulge for the factor-correlation links.
  - **Arrow width ∝ loading**: scales each arrow by its loading (uniform arrows otherwise).

## Notes

- You need enough complete cases for a stable solution, and the model must be identified
  (each factor needs enough indicators).
- With the **DWLS** estimator the fit indices (χ², RMSEA, CFI, TLI) are the robust,
  mean-and-variance-adjusted (Satorra–Bentler / WLSMV) versions, so the degrees of freedom can
  be fractional. The **Unweighted LS (polychoric)** estimator reports the plain (non-robust) ULS
  fit indices and standard errors.
