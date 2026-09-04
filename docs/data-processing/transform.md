# Transform Column

Reshapes one column **in place** (it is replaced, not duplicated). In order, it can:

1. **Map values** — recode specific values to new ones.
2. **Set the target type** — Nominal, Ordinal, or Numeric.
3. For **Ordinal**: define an explicit **category order**, and optionally **flip** the scale
   (reference − x; reference defaults to max + min).
4. For **Numeric**: apply a **normalization** — Z-score, Stanine (normalized 1–9 score from
   percentile ranks), Center, Min-max, Log, or Rank.
5. Set a **color tag** and, optionally, a new name.

Use this to make a column ordinal with a proper order, to reverse-key an item, or to
standardize a variable before analysis.

**Map values** and the **type** dropdown sit side by side, with an **Order** button (ordinal only)
below; the Map values / Order buttons are bold when a mapping or custom order is in effect, and each
pop-up has a **Reset** button. When several columns are selected the shared transform applies to all
of them and the **rename** field is hidden (renaming only makes sense for a single column).
