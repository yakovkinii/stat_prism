# From exploratory to confirmatory factor analysis

A typical scale-development flow: explore the factor structure with EFA, then confirm it with CFA.
StatPrism can hand the EFA solution straight to a CFA so you don't re-enter the structure by hand.

## 1. Explore with EFA

Add an {doc}`../analyses/exploratory-factor-analysis` and select your items. Choose the
**correlation** (Pearson, or **Polychoric** for ordinal items), an **extraction method**, a
**rotation** (an oblique one like *promax* if you expect the factors to correlate), and the
**number of factors** (the scree plot and eigenvalues help you decide — turn on **Show eigenvalues
table** if you want the numbers).

Read the **loadings**: each item should load strongly on one factor and weakly on the others.

## 2. Hand it to a CFA

At the bottom of the EFA settings, click **Create a CFA from this solution**. This creates a new
{doc}`../analyses/confirmatory-factor-analysis` and pre-configures it from the EFA: the same items
and number of factors, each item assigned to the factor it loaded on most strongly, factor
correlation enabled if the EFA rotation was oblique, and a DWLS estimator if the EFA used polychoric
correlations. The new CFA is selected automatically.

(Run the EFA at least once first, so its loadings are available.)

## 3. Refine and confirm

Judge the CFA **fit indices** (chi-square, RMSEA, CFI, TLI, SRMR). To improve fit, turn on the
**Modification hints** and use **Apply cross-loadings** / **Apply correlated residuals** — only the
top few suggestions are listed (with the total in the heading). Tick one to free that parameter and
re-fit; the path diagram then shows the extra loading (dashed) or residual link.

## 4. Score and report

Once you're happy with the model, click **Create a Calculate Scale step per factor** on the CFA to
turn each factor into a {doc}`../data-processing/calculate-scale` step, then analyze or export the
scores as usual.
