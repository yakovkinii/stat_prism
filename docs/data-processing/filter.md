# Filter

Keeps only the rows that match a condition on one column.

- **Numeric columns:** keep rows where the value satisfies a comparison (`<`, `≤`, `=`, `≥`,
  `>`, `≠`) against a value. For `=`/`≠` you may list several values (comma/space separated)
  to keep/exclude any of them. You can also keep rows where the cell **is empty** or **is not
  empty**.
- **Categorical columns:** tick the category values to keep (an *(empty)* option appears when
  the column has blank cells).

Rows that don't match are removed downstream; previewing shows them in red. Toggle the step
off to keep all rows.
