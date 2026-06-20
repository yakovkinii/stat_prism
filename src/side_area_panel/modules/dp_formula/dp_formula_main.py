#  Copyright (c) 2023 StatPrism Team. All rights reserved.

import logging

import numpy as np
import pandas as pd

from src.common.decorators import log_function
from src.data.data import DataColumn
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.common.utility import unique_name
from src.side_area_panel.modules.dp_formula.dp_formula_result import FormulaResult
from src.side_area_panel.modules.dp_formula.dp_formula_ui import Elements


@log_function
def dp_formula_main(elements: Elements, result: FormulaResult, update):
    cfg = result.config
    data = DATA_MANAGER.get_data_from_data_label(
        data_label=cfg.data_source,
        current_result_id=result.unique_id,
    )
    new_data = data.copy()
    # Default to a pass-through so downstream stays valid while inputs are incomplete.
    result.data = new_data

    formula = (cfg.formula or "").strip()
    new_name_raw = (cfg.new_name or "").strip()
    if not new_name_raw:
        elements.new_name.set_alert()
        return result
    if not formula:
        elements.formula.set_alert()
        return result

    df = new_data.get_dataframe()
    try:
        evaluated = df.eval(formula)
    except Exception as e:
        elements.formula.set_alert()
        result.set_error(f"Could not evaluate the formula: {e}")
        return result

    # eval may return a scalar (e.g. a constant expression); broadcast it to a full column.
    if np.isscalar(evaluated) or not hasattr(evaluated, "__len__"):
        evaluated = pd.Series([evaluated] * new_data.n_rows(), index=df.index)
    else:
        evaluated = pd.Series(evaluated, index=df.index)

    new_name = unique_name(new_name_raw, set(new_data.column_names()))
    evaluated = evaluated.copy()
    evaluated.name = new_name

    # initialize_from_series assigns NUMERIC for int/float dtype, NOMINAL otherwise -- exactly
    # the requested "numeric result -> numeric, else nominal" behaviour.
    new_column = DataColumn.initialize_from_series(evaluated)

    column_names = new_data.column_names()
    if column_names:
        new_data.add_column_after(column_names[-1], new_column)
    else:
        new_data.add_column_first(new_column)

    result.data = new_data
    logging.info("Formula column %s added", new_name)
    return result
