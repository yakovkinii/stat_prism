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

# VALIDATED

from typing import Dict, Union

from src.side_area_panel.modules.common.result.base_result import BaseResult
from src.side_area_panel.modules.contingency.contingency_result import ContingencyResult
from src.side_area_panel.modules.correlation.correlation_result import CorrelationResult
from src.side_area_panel.modules.descriptive.descriptive_result import DescriptiveResult
from src.side_area_panel.modules.dp_bootstrap.dp_bootstrap_result import BootstrapResult
from src.side_area_panel.modules.dp_calculate_scale.dp_calculate_scale_result import CalculateScaleResult
from src.side_area_panel.modules.dp_filter.dp_filter_result import FilterDataResult
from src.side_area_panel.modules.dp_formula.dp_formula_result import FormulaResult
from src.side_area_panel.modules.dp_group.dp_group_result import GroupValuesResult
from src.side_area_panel.modules.dp_impute.dp_impute_result import ImputeResult
from src.side_area_panel.modules.dp_invert_scale.dp_invert_scale_result import InvertScaleResult
from src.side_area_panel.modules.dp_onehot.dp_onehot_result import OneHotResult
from src.side_area_panel.modules.dp_outliers.dp_outliers_result import OutliersResult
from src.side_area_panel.modules.dp_preprocess.dp_preprocess_result import PreprocessResult
from src.side_area_panel.modules.dp_select_id.dp_select_id_result import SelectIDResult
from src.side_area_panel.modules.dp_split_multiselect.dp_split_multiselect_result import SplitMultiSelectResult
from src.side_area_panel.modules.dp_transform.dp_transform_result import TransformResult
from src.side_area_panel.modules.exploratory_factor_analysis.exploratory_factor_analysis_result import (
    FactorAnalysisResult,
)
from src.side_area_panel.modules.mean_comparison.mean_comparison_result import MeanComparisonResult
from src.side_area_panel.modules.multiple_response.multiple_response_result import MultipleResponseResult
from src.side_area_panel.modules.paired.paired_result import PairedResult
from src.side_area_panel.modules.power_analysis.power_analysis_result import PowerAnalysisResult
from src.side_area_panel.modules.raw_data.raw_data_result import RawDataResult
from src.side_area_panel.modules.regression.regression_result import RegressionResult
from src.side_area_panel.modules.reliability.reliability_result import ReliabilityResult

RESULTS: Dict[
    int,
    Union[
        BaseResult,
        CorrelationResult,
        DescriptiveResult,
        MeanComparisonResult,
        PairedResult,
        ReliabilityResult,
        RegressionResult,
        ContingencyResult,
        RawDataResult,
        FactorAnalysisResult,
        CalculateScaleResult,
        InvertScaleResult,
        FilterDataResult,
        PreprocessResult,
        GroupValuesResult,
        SelectIDResult,
        OutliersResult,
        PowerAnalysisResult,
        ImputeResult,
        TransformResult,
        FormulaResult,
        BootstrapResult,
        SplitMultiSelectResult,
        OneHotResult,
        MultipleResponseResult,
    ],
] = {}


def get_unique_result_id():
    return max(RESULTS.keys()) + 1 if len(RESULTS) > 0 else 1
