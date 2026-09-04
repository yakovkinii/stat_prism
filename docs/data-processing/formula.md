# Formula

Computes a **new column** from an expression over existing columns — for example
`age / 12` or `score_pre - score_post`. Give the new column a name and the formula; the
result is added as a new column (numeric if the expression yields numbers, otherwise text).

```{important}
Refer to columns by their header. If a column name contains **spaces or punctuation** — which
is normal for Google Forms questions — wrap the name in **backticks**, e.g.
`` `What was your test score?` / 10 ``. Without backticks the formula can't find the column.
```

The formula field is **multiline**, so you can lay a long expression out over several lines
(newlines are ignored when it runs). To enter a column name, type part of it and press **Tab** to
complete it — Tab completes the word before the cursor (from the last space, or from an open
backtick), adding backticks if the name needs them.
