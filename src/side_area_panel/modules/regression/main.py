#  Copyright (c) 2023 StatPrism Team. All rights reserved.


import logging

import numpy as np
import pandas as pd
import statsmodels.api as sm

from src.common.decorators import log_function
from src.common.qcolor import Colors
from src.data.data_manager import DATA_MANAGER
from src.side_area_panel.modules.common.result.html_result import Cell, HTMLTableV2, Row
from src.side_area_panel.modules.common.result.plot_result import (
    Band,
    BandPlotConfig,
    Line,
    LinePlotConfig,
    PlotV2,
    Scatter,
)
from src.side_area_panel.modules.common.utility import format_statistic_apa
from src.side_area_panel.modules.regression.result import (
    RegressionResult,
    RegressionStudyConfig,
)


@log_function
def recalculate_regression_study(elements, result: RegressionResult) -> RegressionResult:
    cfg: RegressionStudyConfig = result.config
    data = DATA_MANAGER.get_data_from_data_label(
        data_label=cfg.data_source,
        current_result_id=result.unique_id,
    )

    cs = cfg.column_selector
    dependent_column = cs[0][0] if cs[0] else None
    independent_columns = cs[1]
    moderator_column = cs[2][0] if cs[2] else None
    mediator_column = cs[3][0] if cs[3] else None

    all_columns = [dependent_column] + independent_columns
    if moderator_column is not None:
        all_columns.append(moderator_column)
    if mediator_column is not None:
        all_columns.append(mediator_column)

    df = data.get_dataframe(columns=all_columns, map_ordinal=True)

    if "const" in all_columns:
        msg = "The column name 'const' is reserved. Please rename the column."
        result.set_placeholder(msg)
        logging.debug(msg)
        return result

    independent_cols = independent_columns.copy()

    if moderator_column:
        logging.info("Performing Moderation Analysis...\n")
        # Add interaction terms between the independent variables and the moderator
        original_independent_cols = independent_cols.copy()
        independent_cols.append(moderator_column)
        for ind_col in original_independent_cols:
            interaction_term = f"{ind_col}&nbsp;*&nbsp;{moderator_column}"
            df[interaction_term] = df[ind_col] * df[moderator_column]
            independent_cols.append(interaction_term)

    mediator_model = None
    if mediator_column:
        logging.info("Performing Mediation Analysis...\n")
        # Step 1: Regress mediator on independent variables
        X_mediator = sm.add_constant(df[independent_cols])
        mediator_model = sm.OLS(df[mediator_column], X_mediator).fit()

        # Step 2: Regress dependent variable on independent variables and mediator
        independent_cols.append(mediator_column)

        # Fit the final regression model

    X = sm.add_constant(df[independent_cols])
    model = sm.OLS(df[dependent_column], X).fit()

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
    if mediator_column:
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
                        Cell(f"{param_name}&nbsp;→&nbsp;{mediator_column}", push_to_left=True),
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
                        Cell(f"{param_name}&nbsp;→&nbsp;{dependent_column}", push_to_left=True),
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
    if len(independent_columns) == 1:
        scatter = Scatter(
            x=df[independent_columns[0]],
            y=df[dependent_column],
            label="Data points",
        )
        items = [scatter]

        x_values_original = np.linspace(df[independent_columns[0]].min(), df[independent_columns[0]].max(), 100)
        x_values_original = pd.DataFrame(
            {
                "const": 1,
                independent_columns[0]: x_values_original,
            }
        )
        if moderator_column:
            mean = df[moderator_column].mean()
            std = df[moderator_column].std()
            colors = Colors()
            for number_of_sds in [-1, 0, 1]:
                x_values = x_values_original.copy()
                x_values[moderator_column] = mean + number_of_sds * std
                x_values[f"{independent_columns[0]}&nbsp;*&nbsp;{moderator_column}"] = (
                    x_values[independent_columns[0]] * x_values[moderator_column]
                )
                line = Line(
                    x=x_values[independent_columns[0]],
                    y=model.predict(x_values),
                    label=f"Regression Line ({number_of_sds} SD)",
                    legend_string=f"Regression Line ({number_of_sds} SD)",
                    config=LinePlotConfig(color=colors.get_color_list()),
                )
                items.append(line)
        elif mediator_column:
            colors = Colors()
            # ============================ DIRECT ================================
            x_values = x_values_original.copy()
            x_values[mediator_column] = df[mediator_column].mean()
            xx = x_values_original[independent_columns[0]]

            # Calculate the confidence intervals
            conf_static = model.bse["const"]
            conf_direct = model.bse[independent_columns[0]]
            conf_mediator_static = mediator_model.bse["const"]
            conf_mediator_dynamic = mediator_model.bse[independent_columns[0]] * abs(xx - xx.mean())
            conf_mediator_total = np.sqrt(conf_mediator_static**2 + conf_mediator_dynamic**2)
            conf_indirect = np.sqrt(
                (conf_mediator_total**2) * (model.params[mediator_column] ** 2)
                + model.bse[mediator_column] ** 2
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
            x_values[mediator_column] = mediator_model.predict(sm.add_constant(x_values))
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
                x=x_values_original[independent_columns[0]],
                y=model.predict(sm.add_constant(x_values)),
                label="Total Effect",
                legend_string="Total Effect",
                config=LinePlotConfig(color=color),
            )
            items.append(plot_band)
            items.append(line_direct)

        else:
            line = Line(
                x=x_values_original[independent_columns[0]],
                y=model.predict(sm.add_constant(x_values_original)),
                label="Regression Line",
            )
            items.append(line)
        plot_result_element = PlotV2(
            items=items,
            title=f"Regression Plot: {dependent_column} vs {independent_columns[0]}",
            plot_title=f"Regression Plot: {dependent_column} vs {independent_columns[0]}",
            x_axis_title=independent_columns[0],
            y_axis_title=dependent_column,
        )

    if plot_result_element:
        result.result_elements.append(plot_result_element)
    return result
