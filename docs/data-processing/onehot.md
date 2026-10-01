# One-hot encoding

Turns a single-select **nominal** column with *k* categories into **0/1 indicator columns**
(one per category, named *column = category*). This lets a categorical variable be used as a
**regression predictor** (regression accepts only numeric/ordinal inputs — see
{doc}`../analyses/regression`).

- By default, all *k* columns are produced.
- Turn **Drop reference category** on to omit one category (*k* − 1 columns) and use it as
  the baseline for regression.

Missing or blank values are encoded as an `—` category. The original column is left
untouched and the indicators are inserted right after it.
