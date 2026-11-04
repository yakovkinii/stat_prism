# Reliability

Estimates the internal consistency of a multi-item scale.

## When to use it

After designing or administering a survey scale, to check whether its items are
internally consistent and whether removing an item would improve consistency.

## Inputs

- **Items**: two or more numeric (or ordinal) columns that make up one scale. Reverse-keyed
  items should be corrected first with **Invert Scale** (see {doc}`../data-processing/invert-scale`).

## Options

- **Coefficient type**: the inter-item correlation used (e.g. Pearson).
- **McDonald's omega**: reports ω in addition to Cronbach's α.
- **Scale name**: a label for the output.
- **Verbal report**: dropdown for how much plain-language interpretation to add (None / Headline /
  Key findings / Significant only / Full). **Headline** gives the one-line scale verdict (α and its
  level); **Key findings** adds ω and flags any item whose removal would raise the coefficient;
  **Full** also reassures when no item would and flags items that correlate weakly with the scale
  total (the item-level discussion needs the *if item removed* table switched on).
- **Verbal indicators** and **Number columns**.

## Output

- **Cronbach's α** (and **McDonald's ω** if requested) with an interpretation.
- An **item statistics** table including item–total correlations and **α if the item is
  removed** (plus **ω if removed** when McDonald's omega is enabled), which flags items that
  weaken the scale. With **Verbal indicators** on, each coefficient gets a plain-language reading,
  and the item table shows a separate "Improves α?" / "Improves ω?" verdict per coefficient.

## Notes

- At least two items are required.
- A high "alpha if removed" relative to the overall alpha suggests an item may not belong on
  the scale.
