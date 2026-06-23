# Transform Column

Reshapes one column **in place** (it is replaced, not duplicated). In order, it can:

1. **Map values** — recode specific values to new ones.
2. **Set the target type** — Nominal, Ordinal, or Numeric.
3. For **Ordinal**: define an explicit **category order**, and optionally **flip** the scale
   (reference − x; reference defaults to max + min).
4. For **Numeric**: apply a **normalisation** — Z-score, Stanine, Center, Min-max, Log, or
   Rank.
5. Set a **colour tag** and, optionally, a new name.

Use this to make a column ordinal with a proper order, to reverse-key an item, or to
standardise a variable before analysis.
