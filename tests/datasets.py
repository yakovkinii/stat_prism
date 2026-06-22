#  Copyright (c) 2023 StatPrism Team. All rights reserved.
"""Names of the committed fixture Excel files and their columns.

The fixtures in ``tests/data/*.xlsx`` are Google-Forms-style exports (leading
``Timestamp`` column, full-question-text headers, comma-separated checkbox answers,
linear scales, blank cells for skipped optionals). They are committed artifacts; the
suite reads them through the program's own reader via ``tests.helpers.load_dataset``.

This module is just constants so tests can reference columns without re-typing the
question text. (No data-generation logic lives in the repo any more.)
"""

MAIN = "main_dataset"
EDGE_TINY = "edge_tiny"
EDGE_CONSTANT = "edge_constant"

# Headers in main_dataset.xlsx (the full question text).
COL_TIMESTAMP = "Timestamp"
COL_AGE = "How old are you?"
COL_INCOME = "What is your monthly income? (USD)"
COL_SCORE = "What was your test score?"
COL_SATISFACTION = "How satisfied are you overall? (1-5)"
COL_PASSED = "Did you pass the exam?"
COL_GENDER = "What is your gender?"
COL_EDUCATION = "Highest education completed"
COL_REGION = "Which region do you live in?"
COL_GROUP = "Assigned group"
COL_FEATURES = "Which features do you use? (select all that apply)"

# The options that appear in the COL_FEATURES checkbox column (for picking the
# indicator columns produced by Split Multi-Select).
FEATURE_OPTIONS = ["Email", "Calendar", "Chat", "Drive", "Meet"]

# Headers in the edge fixtures.
COL_CONSTANT = "Constant answer"
COL_VARYING = "Varying answer"
