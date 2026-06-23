# Formula

Computes a **new column** from an expression over existing columns — for example
`age / 12` or `score_pre - score_post`. Give the new column a name and the formula; the
result is added as a new column (numeric if the expression yields numbers, otherwise text).

```{important}
Refer to columns by their header. If a column name contains **spaces or punctuation** — which
is normal for Google Forms questions — wrap the name in **backticks**, e.g.
`` `What was your test score?` / 10 ``. Without backticks the formula can't find the column.
```
