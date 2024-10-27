import logging
from typing import Dict, Union

import numpy as np
import pandas as pd
import statsmodels.api as sm

from src.common.decorators import log_function
from src.common.result.classes.html_result import Cell, HTMLResultElement, HTMLTable, Row
from src.common.result.classes.plot_result import (
    Band,
    BandPlotConfig,
    Colors,
    Line,
    LinePlotConfig,
    PlotResultElement,
    Scatter,
)
from src.common.utility import format_statistic_apa
from src.modules.regression.result import RegressionResult, RegressionStudyConfig
from src.settings_panel.panels.registry import PanelRegistry


@log_function
def recalculate_regression_study(
    df: pd.DataFrame, result: RegressionResult, ordinal_orders: Dict[str, Dict[Union[int, float, str], int]]
) -> RegressionResult:
    config: RegressionStudyConfig = result.config

    if (config.dependent_column is None) or (len(config.independent_columns) < 1):
        msg = "Please select one Dependent Variable and at least one Independent Variable"
        result.set_placeholder(msg)
        logging.debug(msg)
        return result

    if (config.mediator_column is not None) and (config.moderator_column is not None):
        msg = "Please select either a Mediator or a Moderator, not both"
        result.set_placeholder(msg)
        logging.debug(msg)
        return result

    if len(config.filters) > 0:
        for filter_settings in config.filters:
            query = filter_settings.get_query()
            logging.debug(f"Applying Filter: {query}")
            df = df.query(query)
    else:
        logging.debug("No filter applied")

    all_columns = [config.dependent_column] + config.independent_columns
    if config.moderator_column is not None:
        all_columns.append(config.moderator_column)
    if config.mediator_column is not None:
        all_columns.append(config.mediator_column)

    df = df[all_columns].copy()

    if "const" in all_columns:
        msg = "The column name 'const' is reserved. Please rename the column."
        result.set_placeholder(msg)
        logging.debug(msg)
        return result

    # map ordinal columns
    for col in all_columns:
        if col in ordinal_orders:
            df[col] = df[col].map(ordinal_orders[col])

    independent_cols = config.independent_columns.copy()

    if config.moderator_column:
        logging.info("Performing Moderation Analysis...\n")
        # Add interaction terms between the independent variables and the moderator
        original_independent_cols = independent_cols.copy()
        independent_cols.append(config.moderator_column)
        for ind_col in original_independent_cols:
            interaction_term = f"{ind_col}&nbsp;*&nbsp;{config.moderator_column}"
            df[interaction_term] = df[ind_col] * df[config.moderator_column]
            independent_cols.append(interaction_term)

    mediator_model = None
    if config.mediator_column:
        logging.info("Performing Mediation Analysis...\n")
        # Step 1: Regress mediator on independent variables
        X_mediator = sm.add_constant(df[independent_cols])
        mediator_model = sm.OLS(df[config.mediator_column], X_mediator).fit()

        # Step 2: Regress dependent variable on independent variables and mediator
        independent_cols.append(config.mediator_column)

        # Fit the final regression model

    X = sm.add_constant(df[independent_cols])
    model = sm.OLS(df[config.dependent_column], X).fit()

    # Create fit table
    fit_table = HTMLTable([])
    fit_table.table_caption = "Regression Metrics"
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
    coefficients_table = HTMLTable([])
    coefficients_table.table_caption = "Coefficients"
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
    if config.mediator_column:
        mediator_table = HTMLTable([])
        mediator_table.table_caption = "Path Estimates"
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
                        Cell(f"{param_name}&nbsp;→&nbsp;{config.mediator_column}", push_to_left=True),
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
                        Cell(f"{param_name}&nbsp;→&nbsp;{config.dependent_column}", push_to_left=True),
                        Cell(format_statistic_apa(param_value), center=True),
                        Cell(format_statistic_apa(model.bse[param_name]), center=True),
                        Cell(format_statistic_apa(model.tvalues[param_name]), center=True),
                        Cell(format_statistic_apa(model.pvalues[param_name]), center=True),
                    ]
                )
            )

    html_result_element = HTMLResultElement(
        settings_panel_index=PanelRegistry.HTML_RESULT_ITEM_SETTINGS.settings_stacked_widget_index
    )
    html_result_element.items = [fit_table, coefficients_table]
    if mediator_table:
        html_result_element.items.append(mediator_table)

    plot_result_element = None
    if len(config.independent_columns) == 1:
        plot_result_element = PlotResultElement(
            settings_panel_index=PanelRegistry.PLOT_RESULT_ITEM_SETTINGS.settings_stacked_widget_index,
            tab_title=f"Regression Plot: {config.dependent_column} vs {config.independent_columns[0]}",
            plot_title=f"Regression Plot: {config.dependent_column} vs {config.independent_columns[0]}",
            x_axis_title=config.independent_columns[0],
            y_axis_title=config.dependent_column,
        )
        scatter = Scatter(
            x=df[config.independent_columns[0]],
            y=df[config.dependent_column],
            label="Value",
        )
        plot_result_element.items = [scatter]

        x_values_original = np.linspace(
            df[config.independent_columns[0]].min(), df[config.independent_columns[0]].max(), 100
        )
        x_values_original = pd.DataFrame(
            {
                "const": 1,
                config.independent_columns[0]: x_values_original,
            }
        )
        if config.moderator_column:
            mean = df[config.moderator_column].mean()
            std = df[config.moderator_column].std()
            colors = Colors()
            for number_of_sds in [-1, 0, 1]:
                x_values = x_values_original.copy()
                x_values[config.moderator_column] = mean + number_of_sds * std
                x_values[f"{config.independent_columns[0]}&nbsp;*&nbsp;{config.moderator_column}"] = (
                    x_values[config.independent_columns[0]] * x_values[config.moderator_column]
                )
                line = Line(
                    x=x_values[config.independent_columns[0]],
                    y=model.predict(x_values),
                    label=f"Regression Line ({number_of_sds} SD)",
                    legend_string=f"Regression Line ({number_of_sds} SD)",
                    config=LinePlotConfig(color=colors.get_color_list()),
                )
                plot_result_element.items.append(line)
        elif config.mediator_column:
            colors = Colors()
            # ============================ DIRECT ================================
            x_values = x_values_original.copy()
            x_values[config.mediator_column] = df[config.mediator_column].mean()
            xx = x_values_original[config.independent_columns[0]]

            # Calculate the confidence intervals
            conf_static = model.bse["const"]
            conf_direct = model.bse[config.independent_columns[0]]
            conf_mediator_static = mediator_model.bse["const"]
            conf_mediator_dynamic = mediator_model.bse[config.independent_columns[0]] * abs(xx - xx.mean())
            conf_mediator_total = np.sqrt(conf_mediator_static**2 + conf_mediator_dynamic**2)
            conf_indirect = np.sqrt(
                (conf_mediator_total**2) * (model.params[config.mediator_column] ** 2)
                + model.bse[config.mediator_column] ** 2
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
            plot_result_element.items.append(line_direct)
            plot_result_element.items.append(plot_band)

            # ============================ TOTAL ================================
            x_values = x_values_original.copy()
            x_values[config.mediator_column] = mediator_model.predict(sm.add_constant(x_values))
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
                x=x_values_original[config.independent_columns[0]],
                y=model.predict(sm.add_constant(x_values)),
                label="Total Effect",
                legend_string="Total Effect",
                config=LinePlotConfig(color=color),
            )
            plot_result_element.items.append(plot_band)
            plot_result_element.items.append(line_direct)

        else:
            line = Line(
                x=x_values_original[config.independent_columns[0]],
                y=model.predict(sm.add_constant(x_values_original)),
                label="Regression Line",
            )
            plot_result_element.items.append(line)

    result.result_elements = [html_result_element]
    if plot_result_element:
        result.result_elements.append(plot_result_element)
    return result


def cronbach_alpha(corr_matrix: np.ndarray) -> float:
    k = corr_matrix.shape[0]
    trace = np.trace(corr_matrix)
    matrix_sum = np.sum(corr_matrix)
    alpha = (k / (k - 1)) * (1 - (trace / matrix_sum))
    return alpha
