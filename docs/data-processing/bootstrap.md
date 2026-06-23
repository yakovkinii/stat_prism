# Bootstrap (correlated resampling)

Generates new rows by resampling, optionally inducing a requested **rank correlation**
between variables while preserving each variable's distribution (its marginal). You nominate
a **reference** variable and one or more **drivers** that should correlate with it, and set
the target correlation for each. This is useful for simulations, teaching, and power/what-if
exploration. Because it draws random values, set up your analysis to expect sampling
variation.
