#
#  Copyright (c) 2023 -- 2025 StatPrism Team. All rights reserved.
#

DESCRIPTION = """
<h2> Regression </h2>
<h3> Description </h3>
<div>
    Regression is a statistical method that allows modeling relationships between a dependent variable and one or more
    independent variables.
</div>
<h3> Inputs </h3>

<div>
    <b>Dependent Variable:</b><br>
    The variable to be inferred is called the dependent variable
</div>
<div>
    <b>Independent Variable(s):</b><br>
    The variables used for prediction are called independent variables
</div>
<div>
    <b>Moderator Variable (Optional):</b><br>
    A moderator variable in regression analysis is a third variable that affects the strength or direction of the
    relationship between an independent variable and a dependent variable
</div>
<div>
    <b>Mediator Variable (Optional):</b><br>
    A mediator variable in regression analysis explains the process or mechanism through which an independent variable
    influences a dependent variable
</div>

<div>
</div>
<h3> Interpretation </h3>

<div>
<b>Regression metrics:</b><br>
    R² is the proportion of the variance in the dependent variable that is predictable from the independent
    variable(s). R² = 1 (or 100%): The model explains all the variability of the dependent variable.
    The fit is "perfect" (in the context of linear regression). R² = 0: The model explains none of the variability
    in the dependent variable. This means that the independent variables do not help at all in predicting dependent
    variable. 0 < R² < 1: The closer R² is to 1, the more variance in the dependent variable
    is explained by the independent
    variables. The closer R² is to 0, the less the independent variables explain the variation in the
    dependent variable.
    Adjusted R²: If you're working with multiple regression (more than one independent variable), consider using the
    adjusted R², which adjusts for the number of predictors in the model. Unlike regular R², it penalizes for adding
    variables that do not improve the model significantly. <br>
<b>Coefficients:</b><br>
    The intercept is the predicted value of the dependent variable when all the independent variables are equal to zero.
    SD (Standard Deviation) represents the average amount by which the observed values of the dependent variable deviate
    from their mean. A high SD means the values are widely spread out from the mean, while a low SD means they are close
    to the mean.
    t-value is a measure used to determine whether a particular coefficient (independent variable) in the model is
    statistically significant. It helps assess whether there is enough evidence to suggest that a particular
    independent variable has a meaningful impact on the dependent variable.
    Interpretation of the t-value:
    A large absolute t-value suggests that the corresponding coefficient is significantly different from
    zero, meaning that the independent variable is likely to have a meaningful effect on the dependent variable.
    A high positive or negative t-value indicates that the variable is statistically significant.
    A low t-value (close to 0) means that the variable is likely not contributing significantly to explaining the
    variation in the dependent variable. Significance: The t-value is typically compared to a critical value from
    the t-distribution (which depends on the degrees of freedom and chosen significance level, such as 0.05 or 0.01).
    If the absolute t-value exceeds the critical value, the null hypothesis (which assumes the coefficient is 0,
    i.e., the variable has no effect) is rejected.
    P-value: Often, instead of directly using the t-value, analysts use the corresponding p-value, which tells you
    the probability of observing the t-value if the null hypothesis is true. A small p-value (typically < 0.05)
    indicates that the variable is statistically significant, and the null hypothesis can be rejected.<br>
<b>Path estimates:</b><br>
    Magnitude: The size of the path coefficient tells us how strong the relationship is between two variables.
A larger coefficient indicates a stronger effect.
Direction: The sign of the path coefficient (+ or -) indicates whether the relationship is positive (as one variable
increases, the other increases) or negative (as one variable increases, the other decreases).
Significance: Like in regular regression, we often check the p-values or confidence intervals to determine if the path
coefficients are statistically significant.
</div>

"""
