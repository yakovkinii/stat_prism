# Group Values

Bins a numeric column into ordered groups using split points you provide (e.g. split points
`30, 50` give three bins: under 30, 30–50, and 50+).

- **Split point goes to** controls which side a value exactly on a split point falls on —
  *Higher group* (left-closed `[a, b)`, the default) or *Lower group* (right-closed
  `(a, b]`).
- You can label the bins yourself or let StatPrism name them automatically.

The grouped column is added as a new **ordinal** column, leaving the original untouched.
