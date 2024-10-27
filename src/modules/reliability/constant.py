DESCRIPTION = """
<h2> Reliability Analysis</h2>
<h3> Description </h3>
<div>
    Reliability analysis (Cronbach's Alpha) is used to assess the consistency of a measure.
    Cronbach's Alpha (or tau-equivalent reliability) is a measure of the relationship between a group of questions. 
    The group of questions is called a scale and each question in the group is an item. 
    Cronbach's alpha is therefore a measure of the internal consistency of a scale and therefore of 
    the strength of its reliability.
    Cronbach's Alpha is the correlation between the answers in a questionnaire and can take values between 0 and 1. 
    The higher the average correlation between items, the greater the internal consistency of a test.
    Cronbach's Alpha should not be less than 0.6. Values above 0.7 are considered acceptable. However, 
    the Cronbach's Alpha should preferably not be much higher than 0.9, as this would mean that the questions are 
    "too similar" and therefore you get the same answers to the questions, in which case you could omit questions
    that are too highly correlated and you would not have any loss of information. The table below can be used to 
    interpret Cronbach's Alpha.Furthermore, it is also important to ensure that the questions are all formulated
    in either a positive or a negative way. That is, a high or low value must always mean the same thing.  <br>

<h3> Cronbach's Alpha	Interpretation </h3>
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
