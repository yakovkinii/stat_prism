# One-hot encoding

Turns a single-select **nominal** column with *k* categories into **0/1 indicator columns**
(one per category, named *column = category*). This lets a categorical variable be used as a
**regression predictor** (regression accepts only numeric/ordinal inputs — see
{doc}`../analyses/regression`).

- With **Drop reference category** on (default), one category is omitted (*k* − 1 columns)
  and becomes the baseline — the usual setup for regression.
- Turn it off to keep all *k* columns (useful for plain description).

A row with a missing value gets 0 in every indicator. The original column is left untouched
and the indicators are inserted right after it.
