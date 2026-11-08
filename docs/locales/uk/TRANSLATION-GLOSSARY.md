# StatPrism UA docs — locked translation glossary & house style

## Policy decisions (apply everywhere)
1. **UI labels stay ENGLISH.** The app UI is English-only, so any discrete clickable label the reader sees on screen — dropdown option values, button text, menu items/paths, toggle/checkbox names, slider/control names, example-table column headers — is written in English in the docs, with the surrounding sentence in Ukrainian. KEEP the general approved concept nouns translated even when they also title a control (verbal report=словесний звіт, effect size=розмір ефекту, plots=графіки, factor loadings=факторні навантаження). Revert the specific clickable string, not the concept noun. Examples that stay English: None / Headline / Key findings / Significant only / Full; Detect automatically / Parametric / Non-parametric; Linear (OLS) / Logistic / Multinomial; Center / Min-max / Log / Rank; Tails; Solve for; Paths / Add path / From / To / Type; Sort by factor loadings; Allow factor correlation; Apply cross-loadings; Verbal indicators; Number columns; ML / DWLS / varimax / promax; Pearson / Spearman / Kendall / Polychoric (as selector values).
2. **Transliterate eponyms in prose**, keep abbreviations/indices Latin. In explanatory prose, eponymous names take Ukrainian form: Пірсона, Спірмена, Кендалла, Шапіро-Вілка, Колмогорова-Смирнова, Андерсона-Дарлінга, Лілліефорса, Дарбіна-Вотсона, Махаланобіса, Фішера, Вальда, Стьюдента, Велча, Манна-Вітні, Краскела-Волліса, Вілкоксона, Фрідмана, Левена, Єйтса, МакНемара, Боукера, Коена, Крамера, Тьюкі, Геймса-Хауелла, Данна, Бонферроні, Кука, Варда. Abbreviations/indices stay Latin (RMSEA, CFI, TLI, SRMR, VIF, DWLS, ML). When the same name is a clickable selector value, keep it English (rule 1 wins).
3. **EFA / CFA** = експлораторний / конфірматорний факторний аналіз; EFA/CFA abbreviations stay Latin.

## Register (MOST IMPORTANT)
- Audience: academically inclined Ukrainian readers (psychology/sociology scientists & students).
- Prefer **borrowed / loanword** forms where they read more naturally to a modern academic; do NOT force-nativise.
  Example of the intended taste: "guides" = **гайди** (NOT "настанови"); "placeholder" = **плейсхолдер**; "overfitting" = **оверфітинг**.
- Keep established method names recognizable (English abbreviation in parentheses on first/each mention where listed below).
- Natural, fluent Ukrainian prose — not word-for-word calque. Keep sentences readable, not bureaucratic.
- Do NOT translate: product/brand names (StatPrism), menu/software proper names, Word, APA, CSV, HTML, YouTube, GitHub.

## Named-plot template
English name + Ukrainian type word matching the English suffix:
- `plot` -> `-плот`  |  `chart` -> `-діаграма`  |  `graph` -> `графік`
- box plot -> **box-плот**
- scree plot -> **scree-плот**
- Q-Q plot -> **Q-Q-плот**
- violin plot -> **violin-плот**
- rose plot -> **rose-плот**
- pie chart -> **pie-діаграма**
- bar chart -> **bar-діаграма**
- line graph -> **лінійний графік**
- histogram -> **гістограма**
- heatmap -> **heatmap** (keep English)
- scatter plot -> **діаграма розсіювання** (EXCEPTION, not "scatter-плот")
- generic "plot/graph/figure" -> **графік**

## Density
- density -> **густина розподілу** (ALWAYS, never bare "густина")
- KDE / kernel density -> **оцінка густини розподілу (KDE)**

## Statistics terms
- p-value -> **p-значення**
- effect size -> **розмір ефекту**
- post-hoc (test) -> **post-hoc тест**
- rotation (factor) -> **обертання**
- factor loadings -> **факторні навантаження**
- linkage method -> **метод зв'язування**
- t-test -> **t-тест**
- ANOVA -> **дисперсійний аналіз (ANOVA)**
- SEM -> **структурне моделювання (SEM)**
- two-tailed / one-tailed -> **двосторонній / односторонній**
- contingency table -> **таблиця спряженості**
- omnibus test -> **загальний (omnibus) тест**
- confidence band -> **довірча смуга**
- confidence interval -> **довірчий інтервал**
- residuals -> **залишки**
- standardized residuals -> **стандартизовані залишки**
- fitted / predicted values -> **передбачені значення**
- multicollinearity -> **мультиколінеарність**
- heteroscedasticity -> **гетероскедастичність**
- Cook's distance -> **відстань Кука**
- leverage -> **важіль впливу**
- goodness-of-fit -> **узгодженість моделі**
- overfitting -> **оверфітинг**
- stepwise selection -> **покроковий відбір**
- main effect -> **головний ефект**
- interaction effect -> **ефект взаємодії**
- pairwise comparison -> **попарне порівняння**
- sphericity -> **сферичність**
- repeated measures -> **повторні вимірювання**
- within-subjects / between-subjects -> **для залежних / незалежних вибірок**
- marginal means -> **крайові середні**
- communalities -> **комунальності**
- uniqueness (EFA) -> **унікальність**
- eigenvalue -> **власне значення**
- path diagram -> **path-діаграма**
- latent variable -> **латентна змінна**
- measurement model -> **вимірювальна модель**
- estimator (ML/DWLS) -> **метод оцінювання**
- model fit indices -> **індекси відповідності моделі**
- modification indices -> **індекси модифікації**
- intercept -> **вільний член**
- predictor / outcome -> **незалежна / залежна змінна**
- VIF -> **коефіцієнт інфляції дисперсії (VIF)**
- skewness -> **асиметрія**
- kurtosis -> **ексцес**
- quartile / IQR -> **квартиль / міжквартильний розмах (IQR)**
- percentile -> **процентиль**
- frequency table -> **таблиця частот**
- null / alternative hypothesis -> **нульова / альтернативна гіпотеза**
- degrees of freedom -> **ступені свободи**
- significance level -> **рівень значущості**
- power (statistical) -> **потужність**
- standard deviation -> **стандартне відхилення**
- standard error -> **стандартна похибка**
- variance / covariance -> **дисперсія / коваріація**
- median / mode -> **медіана / мода**
- range (spread) -> **розмах**
- proportion -> **частка**
- sample size -> **обсяг вибірки**
- population -> **генеральна сукупність**
- chi-square -> **хі-квадрат**
- Cramer's V -> **V Крамера**
- value labels -> **мітки значень**
- scale score -> **бал шкали**
- whisker (box plot) -> **вуса**

## Psychometrics / reliability
- Cronbach's alpha -> **альфа Кронбаха**
- McDonald's omega -> **омега Макдональда**
- item-total correlation -> **item-total кореляція**
- reliability / validity -> **надійність / валідність**
- construct -> **конструкт**
- questionnaire item -> **пункт опитувальника**
- Likert scale -> **шкала Лайкерта**
- reverse-keyed scales -> **перевернуті шкали**
- reverse-keyed item -> **перевернутий пункт**
- survey -> **опитування** (note: EN docs drop the survey/questionnaire distinction)
- moderation -> **модерація**
- mediation -> **медіація**
- straightlining -> EN main term is **long-string**; in UA write **long-string (послідовність однакових відповідей)**

## Data processing
- data cleaning -> **очищення даних**
- missing values -> **пропущені значення**
- imputation -> **заповнення пропусків**
- recode -> **перекодування**
- deduplicate -> **видалення дублікатів**
- data source -> **джерело даних**
- outlier -> **викид**
- winsorize -> **вінзоризація**
- standardize / z-score -> **стандартизація / z-оцінка**
- long / wide format -> **довгий / широкий формат**
- merge / join -> **об'єднання**
- aggregate -> **агрегування**
- one-hot encoding -> **one-hot кодування**
- binning / group values -> **групування значень**
- random seed -> **сід**
- bootstrap -> **бутстреп**

## UI / software
- column / row -> **колонка / рядок**
- cell -> **клітинка** (in a table) / **поле** (the drop-target where columns are dragged)
- tab (UI) -> **вкладка**
- panel / pane -> **панель**
- sidebar -> **бічна панель**
- toolbar -> **панель інструментів**
- settings panel -> **панель налаштувань**
- toggle -> **перемикач**
- default (setting) -> **за замовчуванням**
- preview -> **попередній перегляд**
- template -> **шаблон**
- placeholder -> **плейсхолдер**
- clipboard -> **буфер обміну**
- undo / redo -> **undo / redo** (KEEP ENGLISH)
- drag and drop -> **перетягування**
- dropdown -> **dropdown** (keep English)
- checkbox -> **checkbox** (keep English)
- point-and-click -> **point-and-click** (keep English)
- table -> **таблиця**
- legend -> **легенда**
- axis / axis title -> **вісь / назва осі**
- tick labels -> **підписи поділок**
- label (UI) -> **підпис**
- field (form) -> **поле**
- click / select -> **натиснути / вибрати**
- report (HTML) -> **звіт**
- verbal report -> **словесний звіт**
- export to Word -> **експорт у Word**
- dataset -> **набір даних**
- spreadsheet -> **таблиця**
- workflow -> **робочий процес**
- feature -> **функція**
- version -> **версія**
- release -> **реліз**
- open source -> **відкритий код**
- customizable -> **налаштовуваний**
- robust (method) -> **надійний**
- input / output -> **вхідні / вихідні дані**
- desktop app -> **десктопна програма**
- issues (GitHub) -> keep "issues" (e.g. "повідомляти як issues")

## Prose connectives
- note that -> **зверніть увагу, що**
- for example / e.g. -> **наприклад**
- i.e. -> **тобто**
- rule of thumb -> **емпіричне правило**
- trade-off -> **компроміс**
- step-by-step -> **покроково**
- out of the box -> **одразу після встановлення**
- best practice -> **усталена практика**

## Doc navigation
- getting started -> **початок роботи**
- overview -> **огляд**
- worked example -> **розібраний приклад**
- glossary -> **словник термінів**
- FAQ -> **поширені запитання**
- guide / guides -> **гайд / гайди**
- screenshot -> **знімок екрана**
- "See all analyses ->" -> **"Переглянути всі аналізи ->"**
- video walkthrough -> **відеоогляд**
