#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import logging

import numpy as np
import pandas as pd
import statsmodels.api as sm

from src.common.decorators import log_function
from src.common.qcolor import Colors
from src.data.data import Data
from src.modules.common.result.html_result import Cell, HTMLTableV2, Row
from src.modules.common.result.plot_result import (
    Band,
    BandPlotConfig,
    Line,
    LinePlotConfig,
    PlotV2,
    Scatter,
)
from src.modules.common.utility import format_statistic_apa
from src.modules.regression.result import RegressionResult, RegressionStudyConfig


@log_function
def recalculate_regression_study(data: Data, result: RegressionResult) -> RegressionResult:
    cfg: RegressionStudyConfig = result.config
    all_columns = [cfg.dependent_column] + cfg.independent_columns
    if cfg.moderator_column is not None:
        all_columns.append(cfg.moderator_column)
    if cfg.mediator_column is not None:
        all_columns.append(cfg.mediator_column)

    df = data.get_dataframe(filters=result.config.filters, columns=all_columns, map_ordinal=True)

    if "const" in all_columns:
        msg = "The column name 'const' is reserved. Please rename the column."
        result.set_placeholder(msg)
        logging.debug(msg)
        return result

    independent_cols = cfg.independent_columns.copy()

    if cfg.moderator_column:
        logging.info("Performing Moderation Analysis...\n")
        # Add interaction terms between the independent variables and the moderator
        original_independent_cols = independent_cols.copy()
        independent_cols.append(cfg.moderator_column)
        for ind_col in original_independent_cols:
            interaction_term = f"{ind_col}&nbsp;*&nbsp;{cfg.moderator_column}"
            df[interaction_term] = df[ind_col] * df[cfg.moderator_column]
            independent_cols.append(interaction_term)

    mediator_model = None
    if cfg.mediator_column:
        logging.info("Performing Mediation Analysis...\n")
        # Step 1: Regress mediator on independent variables
        X_mediator = sm.add_constant(df[independent_cols])
        mediator_model = sm.OLS(df[cfg.mediator_column], X_mediator).fit()

        # Step 2: Regress dependent variable on independent variables and mediator
        independent_cols.append(cfg.mediator_column)

        # Fit the final regression model

    X = sm.add_constant(df[independent_cols])
    model = sm.OLS(df[cfg.dependent_column], X).fit()

    # Create fit table
    fit_table = HTMLTableV2(table_caption="Regression Metrics")
    fit_table.add_title_row_apa(
        Row(
            [
                Cell(),
                Cell("R<sup>2</sup>", center=True),
                Cell("Adjusted&nbsp;R<sup>2</sup>", center=True),
            ]
        )
    )

    fit_table.add_single_row_apa(
        Row(
            [
                Cell("Model", push_to_left=True),
                Cell(format_statistic_apa(model.rsquared), center=True),
                Cell(format_statistic_apa(model.rsquared_adj), center=True),
            ]
        )
    )

    # Create coefficients table
    coefficients_table = HTMLTableV2(table_caption="Coefficients")
    coefficients_table.add_title_row_apa(
        Row(
            [
                Cell(),
                Cell("Coefficient", center=True),
                Cell("SD", center=True),
                Cell("t-value", center=True),
                Cell("p-value", center=True),
            ]
        )
    )

    for param_name, param_value in model.params.items():
        coefficients_table.add_single_row_apa(
            Row(
                [
                    Cell(param_name if param_name != "const" else "Intercept", push_to_left=True),
                    Cell(format_statistic_apa(param_value), center=True),
                    Cell(format_statistic_apa(model.bse[param_name]), center=True),
                    Cell(format_statistic_apa(model.tvalues[param_name]), center=True),
                    Cell(format_statistic_apa(model.pvalues[param_name]), center=True),
                ]
            )
        )

    mediator_table = None
    if cfg.mediator_column:
        mediator_table = HTMLTableV2(table_caption="Path Estimates")
        mediator_table.add_title_row_apa(
            Row(
                [
                    Cell(),
                    Cell("Coefficient", center=True),
                    Cell("SD", center=True),
                    Cell("t-value", center=True),
                    Cell("p-value", center=True),
                ]
            )
        )

        for param_name, param_value in mediator_model.params.items():
            if param_name == "const":
                continue
            mediator_table.add_single_row_apa(
                Row(
                    [
                        Cell(f"{param_name}&nbsp;→&nbsp;{cfg.mediator_column}", push_to_left=True),
                        Cell(format_statistic_apa(param_value), center=True),
                        Cell(format_statistic_apa(mediator_model.bse[param_name]), center=True),
                        Cell(format_statistic_apa(mediator_model.tvalues[param_name]), center=True),
                        Cell(format_statistic_apa(mediator_model.pvalues[param_name]), center=True),
                    ]
                )
            )
        for i, (param_name, param_value) in enumerate(model.params.items()):
            if param_name == "const":
                continue
            mediator_table.add_single_row_apa(
                Row(
                    [
                        Cell(f"{param_name}&nbsp;→&nbsp;{cfg.dependent_column}", push_to_left=True),
                        Cell(format_statistic_apa(param_value), center=True),
                        Cell(format_statistic_apa(model.bse[param_name]), center=True),
                        Cell(format_statistic_apa(model.tvalues[param_name]), center=True),
                        Cell(format_statistic_apa(model.pvalues[param_name]), center=True),
                    ]
                )
            )
    result.result_elements = []
    result.result_elements.append(fit_table)
    result.result_elements.append(coefficients_table)
    if mediator_table:
        result.result_elements.append(mediator_table)

    plot_result_element = None
    if len(cfg.independent_columns) == 1:
        scatter = Scatter(
            x=df[cfg.independent_columns[0]],
            y=df[cfg.dependent_column],
            label="Data points",
        )
        items = [scatter]

        x_values_original = np.linspace(df[cfg.independent_columns[0]].min(), df[cfg.independent_columns[0]].max(), 100)
        x_values_original = pd.DataFrame(
            {
                "const": 1,
                cfg.independent_columns[0]: x_values_original,
            }
        )
        if cfg.moderator_column:
            mean = df[cfg.moderator_column].mean()
            std = df[cfg.moderator_column].std()
            colors = Colors()
            for number_of_sds in [-1, 0, 1]:
                x_values = x_values_original.copy()
                x_values[cfg.moderator_column] = mean + number_of_sds * std
                x_values[f"{cfg.independent_columns[0]}&nbsp;*&nbsp;{cfg.moderator_column}"] = (
                    x_values[cfg.independent_columns[0]] * x_values[cfg.moderator_column]
                )
                line = Line(
                    x=x_values[cfg.independent_columns[0]],
                    y=model.predict(x_values),
                    label=f"Regression Line ({number_of_sds} SD)",
                    legend_string=f"Regression Line ({number_of_sds} SD)",
                    config=LinePlotConfig(color=colors.get_color_list()),
                )
                items.append(line)
        elif cfg.mediator_column:
            colors = Colors()
            # ============================ DIRECT ================================
            x_values = x_values_original.copy()
            x_values[cfg.mediator_column] = df[cfg.mediator_column].mean()
            xx = x_values_original[cfg.independent_columns[0]]

            # Calculate the confidence intervals
            conf_static = model.bse["const"]
            conf_direct = model.bse[cfg.independent_columns[0]]
            conf_mediator_static = mediator_model.bse["const"]
            conf_mediator_dynamic = mediator_model.bse[cfg.independent_columns[0]] * abs(xx - xx.mean())
            conf_mediator_total = np.sqrt(conf_mediator_static**2 + conf_mediator_dynamic**2)
            conf_indirect = np.sqrt(
                (conf_mediator_total**2) * (model.params[cfg.mediator_column] ** 2)
                + model.bse[cfg.mediator_column] ** 2
            )
            conf_interval = np.sqrt(conf_static**2 + conf_direct**2 + conf_indirect**2)

            yy = model.predict(sm.add_constant(x_values))

            color = colors.get_color_list()
            plot_band = Band(
                x=xx,
                y1=yy - conf_interval,
                y2=yy + conf_interval,
                label="Band: Standard Error",
                config=BandPlotConfig(color=color),
            )
            line_direct = Line(
                x=xx,
                y=yy,
                label="Direct Effect",
                legend_string="Direct Effect (corrected for mediation)",
                config=LinePlotConfig(color=color),
            )
            items.append(line_direct)
            items.append(plot_band)

            # ============================ TOTAL ================================
            x_values = x_values_original.copy()
            x_values[cfg.mediator_column] = mediator_model.predict(sm.add_constant(x_values))
            yy = model.predict(sm.add_constant(x_values))

            color = colors.get_color_list()
            plot_band = Band(
                x=xx,
                y1=yy - conf_interval,
                y2=yy + conf_interval,
                label="Band: Standard Error",
                config=BandPlotConfig(color=color),
            )

            line_direct = Line(
                x=x_values_original[cfg.independent_columns[0]],
                y=model.predict(sm.add_constant(x_values)),
                label="Total Effect",
                legend_string="Total Effect",
                config=LinePlotConfig(color=color),
            )
            items.append(plot_band)
            items.append(line_direct)

        else:
            line = Line(
                x=x_values_original[cfg.independent_columns[0]],
                y=model.predict(sm.add_constant(x_values_original)),
                label="Regression Line",
            )
            items.append(line)
        plot_result_element = PlotV2(
            items=items,
            title=f"Regression Plot: {cfg.dependent_column} vs {cfg.independent_columns[0]}",
            plot_title=f"Regression Plot: {cfg.dependent_column} vs {cfg.independent_columns[0]}",
            x_axis_title=cfg.independent_columns[0],
            y_axis_title=cfg.dependent_column,
        )

    if plot_result_element:
        result.result_elements.append(plot_result_element)
    return result


def cronbach_alpha(corr_matrix: np.ndarray) -> float:
    k = corr_matrix.shape[0]
    trace = np.trace(corr_matrix)
    matrix_sum = np.sum(corr_matrix)
    alpha = (k / (k - 1)) * (1 - (trace / matrix_sum))
    return alpha
