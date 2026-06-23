# Invert Scale

Reverse-scores the selected columns: each value `x` becomes `reference − x`. With no
reference given, it uses `max + min` of the column, so a 1–5 Likert item maps 1↔5, 2↔4,
3↔3. Use it to fix reverse-keyed items before building a scale. The inverted values are
added as new columns.
