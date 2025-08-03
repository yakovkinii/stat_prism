#  Copyright (c) 2023 StatPrism Team. All rights reserved.


DESCRIPTION = """
<h2> Reliability Analysis</h2>
<h3> Description </h3>
<div>
    Reliability analysis (Cronbach's Alpha) is used to assess the consistency of a measure.
</div>

<h3> Cronbach's Alpha	Interpretation </h3>
<div>
> 0,9	excellent <br>
> 0,8	good <br>
> 0,7	acceptable <br>
> 0,6	questionable <br>
> 0,5	poor <br>
< 0,5	unacceptable <br>

As mentioned above, internal consistency only says something about the correlation of the items, but not about whether
the items fit together in terms of content. Cronbach's Alpha only checks whether the items are correlated.
The researcher must therefore ensure that only items that measure the same content are used.
</div>
<h3> Inputs </h3>

<div>
    <b>Underlying Questions:</b><br>
    The questions that form the scale. It is assumed that the scale is a <b>sum</b> of the underlying questions.
</div>
<div>
    <b>Scale (optional):</b><br>
    The scale for which the consistency is measured. Used only to get the name of the scale for reporting.
    A scale is a group of questions used to collectively measure a latent variable.
</div>
<h3> Options </h3>
<div>
    <b>Correlation type:</b><br>
    <ul>
        <li>Pearson: Linear correlation &ndash; continuous variables</li>
        <li>Spearman: Rank correlation &ndash; ordinal data</li>
        <li>Kendall: Rank correlation &ndash; ordinal data, small samples</li>
        <li>Phi: Binary correlation &ndash; binary variables</li>
        <li>Tetrachoric: Binary correlation &ndash; binary variables with underlying continuous variables</li>
    </ul>
</div>
"""
