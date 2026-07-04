#  Copyright (C) 2023-2026  StatPrism Team
#  Balashevych A. K., Petrova N. V., Yakovkin I. I.
#
#  This file is part of StatPrism.
#
#  StatPrism is free software: you can redistribute it and/or modify it under
#  the terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  StatPrism is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
#  A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with
#  StatPrism.  If not, see <https://www.gnu.org/licenses/>.
"""Snapshot tests for the Transform Column DP module."""

import pytest

from src.side_area_panel.modules.dp_transform.dp_transform_main import dp_transform_main
from src.side_area_panel.modules.dp_transform.dp_transform_result import TransformResult, TransformStudyConfig
from tests.datasets import COL_AGE, COL_EDUCATION, COL_SATISFACTION, COL_SCORE, MAIN
from tests.helpers import assert_data_snapshot, load_dataset, run_main


def _config(column, spec):
    return TransformStudyConfig(
        data_source="Auto",
        column_selector=[[column]],
        transform_spec=spec,
    )


def _config_cols(columns, spec):
    """Multi-column selection: one shared spec applied to every column (rename disabled)."""
    return TransformStudyConfig(
        data_source="Auto",
        column_selector=[list(columns)],
        transform_spec=spec,
    )


CASES = [
    ("dp_transform_zscore", _config(COL_SCORE, {"type": "Numeric", "normalize": "Z-score"})),
    ("dp_transform_minmax", _config(COL_SCORE, {"type": "Numeric", "normalize": "Min-max"})),
    ("dp_transform_center", _config(COL_SCORE, {"type": "Numeric", "normalize": "Center"})),
    ("dp_transform_log", _config(COL_SCORE, {"type": "Numeric", "normalize": "Log"})),
    ("dp_transform_rank", _config(COL_SCORE, {"type": "Numeric", "normalize": "Rank"})),
    ("dp_transform_stanine", _config(COL_SCORE, {"type": "Numeric", "normalize": "Stanine"})),
    ("dp_transform_to_nominal", _config(COL_SATISFACTION, {"type": "Nominal"})),
    (
        "dp_transform_to_ordinal",
        _config(COL_EDUCATION, {"type": "Ordinal", "order": ["High school", "Bachelor", "Master", "PhD"]}),
    ),
    # Multi-column: the same spec is applied to every selected column; rename is disabled.
    ("dp_transform_multi_zscore", _config_cols([COL_SCORE, COL_AGE], {"type": "Numeric", "normalize": "Z-score"})),
    ("dp_transform_multi_to_nominal", _config_cols([COL_SATISFACTION, COL_EDUCATION], {"type": "Nominal"})),
]


@pytest.mark.parametrize("name,config", CASES, ids=[c[0] for c in CASES])
def test_transform(name, config):
    result = run_main(dp_transform_main, TransformResult, config, load_dataset(MAIN))
    assert_data_snapshot(result, name)
