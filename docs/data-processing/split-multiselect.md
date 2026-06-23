# Split Multi-Select

Splits a "select all that apply" / checkbox column — where each cell holds a delimited list
of chosen options (e.g. *"Email, Calendar"*) — into one **0/1 indicator column per distinct
option**. A cell gets 1 for an option it contains and 0 otherwise; blank cells get 0
everywhere.

The new columns are numeric, so each can be summarised (its mean is the proportion who
chose that option) or correlated, and together they feed the **Multiple Response** analysis
(see {doc}`../analyses/multiple-response`). Set the **delimiter** (comma by default) and an
optional name **prefix**.
