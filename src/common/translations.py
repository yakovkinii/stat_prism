#  Copyright (c) 2023 StatPrism Team. All rights reserved.
"""Central string table for user-facing, translatable text.

Usage:
    from src.common.translations import t
    t("contingency.table_caption", col1=a, col2=b)

Each entry maps a key to per-language templates. Templates use ``str.format``
placeholders. Missing languages fall back to English. New translatable strings
should be added here rather than branched inline on ``LANGUAGE.is_ua()``.
"""

from src.common.constant import NDASH
from src.common.languages import LANGUAGE

TRANSLATIONS = {
    # ----- Common result components -----
    "common.note": {
        "en": "Note",
        "ua": "Нотатка",
    },
    "common.table": {
        "en": "Table",
        "ua": "Таблиця",
    },
    "common.and": {
        "en": " and ",
        "ua": " та ",
    },
    "common.p_value": {
        "en": "p-value",
        "ua": "p-значення",
    },
    "common.mean": {
        "en": "Mean",
        "ua": "Середнє",
    },
    "common.median": {
        "en": "Median",
        "ua": "Медіана",
    },
    "common.calc_error": {
        "en": "An error occurred during calculation: {error}",
        "ua": "Під час обчислення сталася помилка: {error}",
    },
    "common.configure_hint": {
        "en": "Please configure the analysis using the panel on the right.",
        "ua": "Будь ласка, налаштуйте аналіз на панелі праворуч.",
    },
    "common.msg.select_id": {
        "en": "Select the ID column.",
        "ua": "Оберіть колонку з ідентифікатором.",
    },
    # ----- Contingency -----
    "contingency.table_caption": {
        "en": "Contingency Table between {col1} and {col2}",
        "ua": "Таблиця сполученості між {col1} та {col2}",
    },
    "contingency.total": {
        "en": "Total",
        "ua": "Загалом",
    },
    "contingency.chi2_caption": {
        "en": "Chi-square Test between {col1} and {col2}",
        "ua": "Хі-квадрат тест між {col1} та {col2}",
    },
    "contingency.chi2_note": {
        "en": (
            f"&chi;<sup>2</sup> {NDASH} chi-square statistic, "
            f"N {NDASH} number of respondents, df {NDASH} degrees of freedom"
        ),
        "ua": (
            f"&chi;<sup>2</sup> {NDASH} статистика хі-квадрат, "
            f"N {NDASH} кількість респондентів, df {NDASH} ступені свободи"
        ),
    },
    "contingency.chi2_note_phi": {
        "en": f"&phi; {NDASH} phi coefficient",
        "ua": f"&phi; {NDASH} коефіцієнт фі",
    },
    "contingency.col_pvalue": {
        "en": "p-value",
        "ua": "p-значення",
    },
    "contingency.col_cramer": {
        "en": "Cramer's V",
        "ua": "V Крамера",
    },
    "contingency.rel_weak": {
        "en": "weak relationship",
        "ua": "слабкий зв'язок",
    },
    "contingency.rel_moderate": {
        "en": "moderate relationship",
        "ua": "помірний зв'язок",
    },
    "contingency.rel_strong": {
        "en": "strong relationship",
        "ua": "сильний зв'язок",
    },
    "contingency.significant": {
        "en": "A significant relationship was found between {col1} and {col2}: {stats}.",
        "ua": "Знайдено статистично значущий зв'язок між {col1} та {col2}: {stats}.",
    },
    "contingency.not_significant": {
        "en": "No significant relationship was found between {col1} and {col2}: {stats}.",
        "ua": "Не знайдено статистично значущого зв'язку між {col1} та {col2}: {stats}.",
    },
    "contingency.cramer_text": {
        "en": "The {name} = {v}, indicating a {interpretation} between {col1} and {col2}.",
        "ua": "{name} = {v}, що свідчить про {interpretation} між {col1} та {col2}.",
    },
    "contingency.plot_title": {
        "en": "Distribution of {col1} by {col2}",
        "ua": "Розподіл «{col1}» за «{col2}»",
    },
    "contingency.plot_y_axis": {
        "en": "{col} (%)",
        "ua": "{col} (%)",
    },
    "contingency.fisher_caption": {
        "en": "Fisher's Exact Test between {col1} and {col2}",
        "ua": "Точний тест Фішера між {col1} та {col2}",
    },
    "contingency.fisher_text": {
        "en": "Fisher's exact test: odds ratio = {odds}, {p}.",
        "ua": "Точний тест Фішера: відношення шансів = {odds}, {p}.",
    },
    "contingency.error.select_two": {
        "en": "Please select two variables (one for each axis).",
        "ua": "Будь ласка, оберіть дві змінні (по одній на кожну вісь).",
    },
    "contingency.error.distinct": {
        "en": "Please select two different variables.",
        "ua": "Будь ласка, оберіть дві різні змінні.",
    },
    "contingency.error.min_categories": {
        "en": "Each variable must have at least two distinct categories.",
        "ua": "Кожна змінна повинна мати щонайменше дві різні категорії.",
    },
    "contingency.error.no_data": {
        "en": "No complete observations for the selected variables.",
        "ua": "Немає повних спостережень для обраних змінних.",
    },
    "contingency.description": {
        "en": (
            "<h2>Contingency Table &amp; Chi-square Test</h2>"
            "<h3>Description</h3>"
            "<div>Cross-tabulates two categorical variables and tests whether they are "
            "associated, using Pearson's chi-square test of independence.</div>"
            "<div>It reports the contingency table with row/column totals, the chi-square "
            "statistic with its p-value, an effect size (&phi; for 2&times;2 tables, "
            "otherwise Cramer's V), and a 100% stacked-bar plot of the distribution. For "
            "2&times;2 tables Fisher's exact test is added when expected counts are small.</div>"
        ),
        "ua": (
            "<h2>Таблиця сполученості та тест хі-квадрат</h2>"
            "<h3>Опис</h3>"
            "<div>Будує таблицю сполученості двох категоріальних змінних і перевіряє "
            "наявність зв'язку між ними за допомогою тесту незалежності хі-квадрат Пірсона.</div>"
            "<div>Виводить таблицю сполученості з підсумками за рядками та стовпцями, "
            "статистику хі-квадрат із p-значенням, розмір ефекту (&phi; для таблиць 2&times;2, "
            "інакше V Крамера) та стовпчасту діаграму розподілу (100%). Для таблиць 2&times;2 "
            "додається точний тест Фішера, якщо очікувані частоти малі.</div>"
        ),
    },
    # ----- T-test / ANOVA (mean comparison) -----
    # Table captions
    "ttest.caption.mann_whitney": {
        "en": "Mann-Whitney U test",
        "ua": "U-критерій Манна–Уітні",
    },
    "ttest.caption.ttest_independent": {
        "en": "Independent Samples T-test",
        "ua": "t-критерій для незалежних вибірок",
    },
    "ttest.caption.welch_ttest": {
        "en": "Welch's T-test results",
        "ua": "Результати t-критерію Велча",
    },
    "ttest.caption.kruskal": {
        "en": "Kruskal-Wallis test",
        "ua": "Критерій Краскела–Уолліса",
    },
    "ttest.caption.welch_anova": {
        "en": "Welch's ANOVA results",
        "ua": "Результати ANOVA Велча",
    },
    "ttest.caption.one_way_anova": {
        "en": "One-Way ANOVA results",
        "ua": "Результати однофакторного дисперсійного аналізу (ANOVA)",
    },
    "ttest.caption.dunn": {
        "en": "Dunn's post-hoc test results",
        "ua": "Результати апостеріорного тесту Данна",
    },
    "ttest.caption.tamhane": {
        "en": "Tamhane's T2 post-hoc test results",
        "ua": "Результати апостеріорного тесту Тамхейна T2",
    },
    "ttest.caption.tukey": {
        "en": "Tukey's HSD post-hoc test results",
        "ua": "Результати апостеріорного тесту Тьюкі (HSD)",
    },
    "ttest.caption.shapiro": {
        "en": "Shapiro-Wilk normality test",
        "ua": "Критерій нормальності Шапіро–Уілка",
    },
    "ttest.caption.levene": {
        "en": "Levene's test for homogeneity of variance",
        "ua": "Критерій Лівіня для однорідності дисперсій",
    },
    # Column headers (statistic names)
    "ttest.col.mann_whitney_u": {
        "en": "Mann-Whitney U",
        "ua": "U Манна–Уітні",
    },
    "ttest.col.t_statistic": {
        "en": "t-statistic",
        "ua": "t-статистика",
    },
    "ttest.col.f_statistic": {
        "en": "F-statistic",
        "ua": "F-статистика",
    },
    "ttest.col.kruskal_h": {
        "en": "Kruskal-Wallis H",
        "ua": "H Краскела–Уолліса",
    },
    "ttest.col.welch_f": {
        "en": "Welch's F",
        "ua": "F Велча",
    },
    "ttest.col.levene_f": {
        "en": "Levene's F",
        "ua": "F Лівіня",
    },
    "ttest.col.shapiro_w": {
        "en": "Shapiro-Wilk W",
        "ua": "W Шапіро–Уілка",
    },
    # Test names (used in verbal report and post-hoc sentences)
    "ttest.test.mann_whitney": {
        "en": "Mann-Whitney U test",
        "ua": "U-критерій Манна–Уітні",
    },
    "ttest.test.ttest_independent": {
        "en": "Independent Samples T-test",
        "ua": "t-критерій для незалежних вибірок",
    },
    "ttest.test.welch_ttest": {
        "en": "Welch's T-test",
        "ua": "t-критерій Велча",
    },
    "ttest.test.kruskal": {
        "en": "Kruskal-Wallis test",
        "ua": "критерій Краскела–Уолліса",
    },
    "ttest.test.welch_anova": {
        "en": "Welch's ANOVA",
        "ua": "ANOVA Велча",
    },
    "ttest.test.one_way_anova": {
        "en": "One-Way ANOVA",
        "ua": "однофакторний дисперсійний аналіз (ANOVA)",
    },
    "ttest.test.shapiro": {
        "en": "Shapiro-Wilk test",
        "ua": "критерій Шапіро–Уілка",
    },
    "ttest.test.levene": {
        "en": "Levene's test",
        "ua": "критерій Лівіня",
    },
    # What the test checks
    "ttest.check.diff_groups": {
        "en": "difference between the groups",
        "ua": "відмінність між групами",
    },
    "ttest.check.equality_means": {
        "en": "equality of means",
        "ua": "рівність середніх значень",
    },
    "ttest.check.normality": {
        "en": "normality within groups",
        "ua": "нормальність розподілу в групах",
    },
    "ttest.check.homogeneity": {
        "en": "homogeneity of variance",
        "ua": "однорідність дисперсій",
    },
    # Conclusions about variables
    "ttest.prop.sig_diff": {
        "en": "are significantly different across the groups",
        "ua": "статистично значущо відрізняються між групами",
    },
    "ttest.prop.not_sig_diff": {
        "en": "are not significantly different across the groups",
        "ua": "статистично значущо не відрізняються між групами",
    },
    "ttest.prop.diff_means": {
        "en": "have different means",
        "ua": "мають різні середні значення",
    },
    "ttest.prop.equal_means": {
        "en": "have equal means",
        "ua": "мають рівні середні значення",
    },
    "ttest.prop.normal": {
        "en": "are normally distributed (p > 0.05)",
        "ua": "розподілені нормально (p > 0.05)",
    },
    "ttest.prop.not_normal": {
        "en": "are not normally distributed (p < 0.05)",
        "ua": "розподілені ненормально (p < 0.05)",
    },
    "ttest.prop.homogeneous": {
        "en": "have homogeneity of variance",
        "ua": "мають однорідні дисперсії",
    },
    "ttest.prop.inhomogeneous": {
        "en": "have inhomogeneous variance",
        "ua": "мають неоднорідні дисперсії",
    },
    # Verbal report connectives
    "ttest.verbal.compact": {
        "en": "[Compact description]",
        "ua": "[Стислий опис]",
    },
    "ttest.verbal.detailed": {
        "en": "[Detailed description]",
        "ua": "[Детальний опис]",
    },
    "ttest.verbal.used_to_check": {
        "en": "The {test_name} was used to check the {test_check} and has shown that ",
        "ua": "Застосовано {test_name} для перевірки ({test_check}). Показано, що ",
    },
    "ttest.verbal.on_other_hand": {
        "en": " On the other hand, ",
        "ua": " З іншого боку, ",
    },
    "ttest.verbal.has_shown": {
        "en": "The {test_name} has shown that {variable} {property}{stats}. ",
        "ua": "{test_name}: {variable} {property}{stats}. ",
    },
    "ttest.verbal.for_group": {
        "en": "For the group {group}, {stats}. ",
        "ua": "Для групи «{group}»: {stats}. ",
    },
    # Post-hoc
    "ttest.posthoc.dunn": {
        "en": "Dunn's",
        "ua": "Данна",
    },
    "ttest.posthoc.tamhane": {
        "en": "Tamhane's T2",
        "ua": "Тамхейна T2",
    },
    "ttest.posthoc.tukey": {
        "en": "Tukey's HSD",
        "ua": "Тьюкі (HSD)",
    },
    "ttest.posthoc_sentence": {
        "en": (
            "The {name} post-hoc test for {col} has revealed a significant "
            "difference between the following groups: {groups}."
        ),
        "ua": (
            "Апостеріорний тест {name} для «{col}» виявив статистично значущу "
            "різницю між такими групами: {groups}."
        ),
    },
    "ttest.group_pair": {
        "en": "{a} and {b} ({p})",
        "ua": "{a} та {b} ({p})",
    },
    # Plots
    "ttest.plot.distribution": {
        "en": "Distribution of {col}",
        "ua": "Розподіл «{col}»",
    },
    "ttest.plot.distribution_tab": {
        "en": "Plot: Distribution of {col}",
        "ua": "Графік: розподіл «{col}»",
    },
    "ttest.plot.density": {
        "en": "Density",
        "ua": "Щільність",
    },
    # Validation / error messages
    "ttest.error.one_grouping": {
        "en": "Please select exactly one grouping column.",
        "ua": "Будь ласка, оберіть рівно один стовпець групування.",
    },
    "ttest.error.not_enough_groups": {
        "en": "The grouping column needs at least two distinct values (found: {groups}).",
        "ua": "Стовпець групування повинен мати щонайменше два різні значення (знайдено: {groups}).",
    },
    "ttest.error.auto_no_assumptions": {
        "en": (
            "Assumption checks are off and the method is Automatic, so the appropriate test "
            "cannot be determined. Choose a method or enable assumption checks."
        ),
        "ua": (
            "Перевірку припущень вимкнено, а метод — «Визначити автоматично», тому неможливо "
            "обрати відповідний тест. Оберіть метод або увімкніть перевірку припущень."
        ),
    },
    "ttest.error.insufficient_population": {
        "en": "Some groups have too few observations (at least 3 required): {groups}.",
        "ua": "Деякі групи містять замало спостережень (потрібно щонайменше 3): {groups}.",
    },
    # Module help (shown as the placeholder before the analysis is configured)
    "ttest.description": {
        "en": (
            "<h2>Mean Comparison (Independent Samples)</h2>"
            "<h3>Description</h3>"
            "<div>Compare the means of two or more groups to determine if they are "
            "significantly different.</div>"
            "<div>If the grouping column has two unique values, the t-test family is used:"
            "<ul>"
            "<li>If the variable is non-numerical, or not normally distributed (Shapiro-Wilk "
            "test), the Mann-Whitney U test is used.</li>"
            "<li>If homogeneity of variance (Levene's test) is violated, Welch's t-test is used.</li>"
            "<li>Otherwise, the independent-samples t-test is used.</li>"
            "</ul></div>"
            "<div>If the grouping column has more than two unique values, the ANOVA family is used:"
            "<ul>"
            "<li>If the variable is non-numerical, or not normally distributed (Shapiro-Wilk "
            "test), the Kruskal-Wallis test is used.</li>"
            "<li>If homogeneity of variance (Levene's test) is violated, Welch's ANOVA is used.</li>"
            "<li>Otherwise, one-way ANOVA is used.</li>"
            "</ul></div>"
            "<h3>Inputs</h3>"
            "<div><b>Variable(s):</b><br>The variable(s) to compare.</div>"
            "<div><b>Grouping Column:</b><br>The column that defines the groups to compare "
            "(such as respondent's sex or age group).</div>"
        ),
        "ua": (
            "<h2>Порівняння середніх (незалежні вибірки)</h2>"
            "<h3>Опис</h3>"
            "<div>Порівняння середніх двох або більше груп для визначення, чи відрізняються "
            "вони статистично значущо.</div>"
            "<div>Якщо стовпець групування має два унікальні значення, використовується "
            "родина t-критерію:"
            "<ul>"
            "<li>Якщо змінна нечислова або не розподілена нормально (критерій Шапіро–Уілка), "
            "використовується U-критерій Манна–Уітні.</li>"
            "<li>Якщо порушено однорідність дисперсій (критерій Лівіня), використовується "
            "t-критерій Велча.</li>"
            "<li>Інакше використовується t-критерій для незалежних вибірок.</li>"
            "</ul></div>"
            "<div>Якщо стовпець групування має більше двох унікальних значень, "
            "використовується родина ANOVA:"
            "<ul>"
            "<li>Якщо змінна нечислова або не розподілена нормально (критерій Шапіро–Уілка), "
            "використовується критерій Краскела–Уолліса.</li>"
            "<li>Якщо порушено однорідність дисперсій (критерій Лівіня), використовується "
            "ANOVA Велча.</li>"
            "<li>Інакше використовується однофакторний дисперсійний аналіз (ANOVA).</li>"
            "</ul></div>"
            "<h3>Вхідні дані</h3>"
            "<div><b>Змінна(і):</b><br>Змінні для порівняння.</div>"
            "<div><b>Стовпець групування:</b><br>Стовпець, що визначає групи для порівняння "
            "(наприклад, стать або вікова група респондента).</div>"
        ),
    },
    # ----- Reliability -----
    "reliability.caption.cronbach": {
        "en": "Cronbach's α",
        "ua": "α Кронбаха",
    },
    "reliability.caption.coefficients": {"en": "Reliability", "ua": "Надійність"},
    "reliability.col.coefficient": {"en": "Coefficient", "ua": "Коефіцієнт"},
    "reliability.col.value": {"en": "Value", "ua": "Значення"},
    "reliability.row.omega": {"en": "McDonald's ω", "ua": "ω Макдональда"},
    "reliability.report.omega": {
        "en": "McDonald's ω = {omega} ({level}). ",
        "ua": "ω Макдональда = {omega} ({level}). ",
    },
    "reliability.msg.binary_required": {
        "en": "All columns must have at most 2 unique values for the selected correlation type",
        "ua": "Усі стовпці повинні мати щонайбільше 2 унікальні значення для обраного типу кореляції",
    },
    "reliability.description": {
        "en": (
            "Reliability analysis estimates the internal consistency of a scale &mdash; how "
            "closely its items measure the same underlying construct &mdash; with Cronbach's "
            "&alpha;. Values closer to 1 indicate more consistent items. Select the items that "
            "make up the scale; the optional Scale name only labels the scale in the output."
        ),
        "ua": (
            "Аналіз надійності оцінює внутрішню узгодженість шкали &mdash; наскільки її пункти "
            "вимірюють той самий латентний конструкт &mdash; за допомогою альфи Кронбаха. "
            "Значення, ближчі до 1, свідчать про більшу узгодженість пунктів. Виберіть пункти, "
            "що утворюють шкалу; необов'язкова «Назва шкали» лише підписує шкалу у звіті."
        ),
    },
    "reliability.error.min_items": {
        "en": "Select at least two items for the scale.",
        "ua": "Виберіть щонайменше два пункти для шкали.",
    },
    "reliability.caption.item_deleted": {
        "en": "Reliability if item removed",
        "ua": "Надійність за вилучення пункту",
    },
    "reliability.col.item": {"en": "Item", "ua": "Пункт"},
    "reliability.col.item_total": {"en": "Item&ndash;total r", "ua": "Кореляція пункт&ndash;сума"},
    "reliability.col.alpha_deleted": {"en": "&alpha; if removed", "ua": "&alpha; за вилучення"},
    "reliability.col.interpretation": {"en": "Interpretation", "ua": "Інтерпретація"},
    "reliability.col.improves": {"en": "Improves &alpha;?", "ua": "Покращує &alpha;?"},
    "reliability.scale_default": {"en": "The scale", "ua": "Шкала"},
    "reliability.interpret.excellent": {"en": "excellent", "ua": "відмінну"},
    "reliability.interpret.good": {"en": "good", "ua": "добру"},
    "reliability.interpret.acceptable": {"en": "acceptable", "ua": "прийнятну"},
    "reliability.interpret.questionable": {"en": "questionable", "ua": "сумнівну"},
    "reliability.interpret.poor": {"en": "poor", "ua": "низьку"},
    "reliability.interpret.unacceptable": {"en": "unacceptable", "ua": "неприйнятну"},
    "reliability.report.main": {
        "en": "{scale} ({n} items) shows {level} internal consistency, Cronbach's α = {alpha}. ",
        "ua": "{scale} ({n} пунктів) має {level} внутрішню узгодженість, альфа Кронбаха = {alpha}. ",
    },
    "reliability.report.item_improve": {
        "en": "Removing {items} would increase α. ",
        "ua": "Вилучення {items} підвищило б α. ",
    },
    "reliability.report.item_none": {
        "en": "Removing any single item would not increase α. ",
        "ua": "Вилучення будь-якого окремого пункту не підвищило б α. ",
    },
    # ----- Regression -----
    "regression.description": {
        "en": (
            "Linear regression (ordinary least squares) models a numeric dependent variable as "
            "a linear combination of one or more independent variables. R&sup2; is the share of "
            "the dependent variable's variance the model explains; each coefficient is the "
            "expected change in the dependent variable per one-unit increase in that predictor, "
            "holding the others constant. Optionally add a moderator (its interaction with the "
            "predictors) or a mediator (an intermediate variable on the path)."
        ),
        "ua": (
            "Лінійна регресія (метод найменших квадратів) моделює числову залежну змінну як "
            "лінійну комбінацію однієї чи кількох незалежних змінних. R&sup2; &mdash; частка "
            "дисперсії залежної змінної, яку пояснює модель; кожен коефіцієнт &mdash; очікувана "
            "зміна залежної змінної на одиницю зростання предиктора за інших незмінних. За "
            "потреби додайте модератор (його взаємодію з предикторами) або медіатор (проміжну "
            "змінну на шляху впливу)."
        ),
    },
    "regression.error.no_dependent": {
        "en": "Select a dependent variable.",
        "ua": "Виберіть залежну змінну.",
    },
    "regression.error.no_independent": {
        "en": "Select at least one independent variable.",
        "ua": "Виберіть щонайменше одну незалежну змінну.",
    },
    "regression.error.const_reserved": {
        "en": "The column name 'const' is reserved. Please rename the column.",
        "ua": "Назва стовпця «const» зарезервована. Будь ласка, перейменуйте стовпець.",
    },
    "regression.error.insufficient_data": {
        "en": "Not enough complete rows for the number of predictors.",
        "ua": "Недостатньо повних рядків для такої кількості предикторів.",
    },
    "regression.caption.fit": {"en": "Model fit", "ua": "Якість моделі"},
    "regression.caption.coefficients": {"en": "Coefficients", "ua": "Коефіцієнти"},
    "regression.caption.paths": {"en": "Path estimates", "ua": "Оцінки шляхів"},
    "regression.row.model": {"en": "Model", "ua": "Модель"},
    "regression.row.intercept": {"en": "Intercept", "ua": "Вільний член"},
    "regression.col.n": {"en": "N", "ua": "N"},
    "regression.col.adj_r2": {"en": "Adjusted R<sup>2</sup>", "ua": "Скориговане R<sup>2</sup>"},
    "regression.col.f": {"en": "F", "ua": "F"},
    "regression.col.b": {"en": "B", "ua": "B"},
    "regression.col.se": {"en": "SE", "ua": "SE"},
    "regression.col.beta": {"en": "β", "ua": "β"},
    "regression.col.ci": {"en": "95% CI", "ua": "95% ДІ"},
    "regression.col.t": {"en": "t", "ua": "t"},
    "regression.report.fit": {
        "en": (
            "The model explains {pct}% of the variance in {dv} "
            "(R² = {r2}, adjusted R² = {adj}); F({df1}, {df2}) = {f}, {p}. "
        ),
        "ua": (
            "Модель пояснює {pct}% дисперсії «{dv}» "
            "(R² = {r2}, скориговане R² = {adj}); F({df1}, {df2}) = {f}, {p}. "
        ),
    },
    "regression.report.significant": {
        "en": "The overall model is statistically significant. ",
        "ua": "Модель загалом статистично значуща. ",
    },
    "regression.report.not_significant": {
        "en": "The overall model is not statistically significant. ",
        "ua": "Модель загалом статистично незначуща. ",
    },
    "regression.report.predictors": {
        "en": "Significant predictors: {items}. ",
        "ua": "Значущі предиктори: {items}. ",
    },
    "regression.report.predictors_none": {
        "en": "No individual predictor is statistically significant. ",
        "ua": "Жоден окремий предиктор не є статистично значущим. ",
    },
    "regression.dir.positive": {"en": "positive", "ua": "позитивний"},
    "regression.dir.negative": {"en": "negative", "ua": "негативний"},
    "regression.report.coef_intro": {
        "en": (
            "Each B is the expected change in {dv} per one-unit increase in that predictor, "
            "with the other predictors held constant; it is significant when p &lt; .05. "
        ),
        "ua": (
            "Кожен B &mdash; очікувана зміна «{dv}» на одиницю зростання предиктора за інших "
            "незмінних; він значущий, коли p &lt; .05. "
        ),
    },
    "regression.report.coef_sig": {
        "en": "Significant predictors of {dv}: {items}. ",
        "ua": "Значущі предиктори «{dv}»: {items}. ",
    },
    "regression.report.coef_none": {
        "en": "No predictor significantly predicts {dv} once the others are held constant. ",
        "ua": "Жоден предиктор не передбачає «{dv}» значущо за інших незмінних. ",
    },
    "regression.report.med_intro": {
        "en": (
            "Mediation splits each predictor's effect on {dv} into a direct path and an "
            "indirect path through {mediator}. "
        ),
        "ua": (
            "Медіація розкладає вплив кожного предиктора на «{dv}» на прямий шлях і непрямий "
            "шлях через «{mediator}». "
        ),
    },
    "regression.report.med_b": {
        "en": "{mediator} predicts {dv} with b = {b} ({p}). ",
        "ua": "«{mediator}» передбачає «{dv}» з b = {b} ({p}). ",
    },
    "regression.report.med_indirect": {
        "en": "Estimated indirect effects (a&times;b): {items}. ",
        "ua": "Оцінені непрямі ефекти (a&times;b): {items}. ",
    },
    "regression.plot.title": {
        "en": "Regression: {dv} vs {iv}",
        "ua": "Регресія: «{dv}» від «{iv}»",
    },
    "regression.plot.data": {"en": "Data points", "ua": "Спостереження"},
    "regression.plot.line": {"en": "Regression line", "ua": "Лінія регресії"},
    "regression.plot.line_sd": {
        "en": "Regression line ({sd} SD)",
        "ua": "Лінія регресії ({sd} SD)",
    },
    "regression.plot.direct": {
        "en": "Direct effect (corrected for mediation)",
        "ua": "Прямий ефект (з поправкою на медіацію)",
    },
    "regression.plot.total": {"en": "Total effect", "ua": "Загальний ефект"},
    "regression.plot.band": {"en": "Standard error", "ua": "Стандартна похибка"},
    "regression.diag.vif_caption": {"en": "Multicollinearity (VIF)", "ua": "Мультиколінеарність (VIF)"},
    "regression.col.vif": {"en": "VIF", "ua": "VIF"},
    "regression.diag.concern": {"en": "Concern", "ua": "Ризик"},
    "regression.vif.low": {"en": "low", "ua": "низький"},
    "regression.vif.moderate": {"en": "moderate", "ua": "помірний"},
    "regression.vif.high": {"en": "high", "ua": "високий"},
    "regression.report.vif_ok": {
        "en": "All VIFs are below 5, indicating low multicollinearity. ",
        "ua": "Усі VIF нижче 5, що вказує на низьку мультиколінеарність. ",
    },
    "regression.report.vif_high": {
        "en": "High multicollinearity (VIF ≥ 10): {items}. ",
        "ua": "Висока мультиколінеарність (VIF ≥ 10): {items}. ",
    },
    "regression.diag.resid_fitted": {"en": "Residuals vs fitted", "ua": "Залишки від прогнозу"},
    "regression.diag.fitted": {"en": "Fitted values", "ua": "Прогнозовані значення"},
    "regression.diag.residual": {"en": "Residual", "ua": "Залишок"},
    "regression.diag.zero": {"en": "Zero", "ua": "Нуль"},
    "regression.diag.points": {"en": "Residuals", "ua": "Залишки"},
    "regression.diag.qq": {"en": "Normal Q-Q of residuals", "ua": "Нормальний Q-Q залишків"},
    "regression.diag.theoretical": {"en": "Theoretical quantiles", "ua": "Теоретичні квантилі"},
    "regression.diag.sample": {"en": "Sample quantiles", "ua": "Вибіркові квантилі"},
    "regression.diag.ref": {"en": "Reference", "ua": "Опорна лінія"},
    # ----- Exploratory Factor Analysis -----
    "efa.description": {
        "en": (
            "Exploratory factor analysis (EFA) uncovers a small number of latent factors that "
            "explain the correlations among the observed variables. It reports the sampling "
            "adequacy (KMO &amp; Bartlett), the eigenvalues, the factor loadings with each "
            "variable's communality/uniqueness, and &mdash; for oblique rotations &mdash; the "
            "factor correlations and structure matrix. Interpret variables using the loadings "
            "(pattern) matrix."
        ),
        "ua": (
            "Експлораторний факторний аналіз (EFA) виявляє невелику кількість латентних "
            "факторів, що пояснюють кореляції між спостережуваними змінними. Він подає "
            "адекватність вибірки (KMO та Бартлетт), власні значення, факторні навантаження з "
            "спільністю/унікальністю кожної змінної та &mdash; для косокутних обертань &mdash; "
            "кореляції факторів і структурну матрицю. Інтерпретуйте змінні за матрицею "
            "навантажень (патерну)."
        ),
    },
    "efa.error.min_variables": {
        "en": "Select at least two variables.",
        "ua": "Виберіть щонайменше дві змінні.",
    },
    "efa.error.insufficient": {
        "en": "Not enough complete data for factor analysis.",
        "ua": "Недостатньо повних даних для факторного аналізу.",
    },
    "efa.error.too_many_factors": {
        "en": "Number of factors ({m}) cannot exceed the number of variables ({n}).",
        "ua": "Кількість факторів ({m}) не може перевищувати кількість змінних ({n}).",
    },
    "efa.caption.kmo": {"en": "KMO and Bartlett's test", "ua": "Тест KMO і Бартлетта"},
    "efa.caption.eigen": {"en": "Eigenvalues (correlation matrix)", "ua": "Власні значення (кореляційна матриця)"},
    "efa.caption.loadings": {"en": "Factor loadings ({rotation})", "ua": "Факторні навантаження ({rotation})"},
    "efa.caption.phi": {"en": "Factor correlation matrix (Φ)", "ua": "Матриця кореляцій факторів (Φ)"},
    "efa.caption.structure": {"en": "Structure matrix", "ua": "Структурна матриця"},
    "efa.col.component": {"en": "Component", "ua": "Компонента"},
    "efa.col.eigenvalue": {"en": "Eigenvalue", "ua": "Власне значення"},
    "efa.col.variance_pct": {"en": "% of variance", "ua": "% дисперсії"},
    "efa.col.cumulative": {"en": "Cumulative %", "ua": "Накопичений %"},
    "efa.col.variable": {"en": "Variable", "ua": "Змінна"},
    "efa.col.communality": {"en": "Communality", "ua": "Спільність"},
    "efa.col.uniqueness": {"en": "Uniqueness", "ua": "Унікальність"},
    "efa.row.kmo": {"en": "KMO (overall)", "ua": "KMO (загальний)"},
    "efa.row.msa": {"en": "MSA: {name}", "ua": "MSA: {name}"},
    "efa.row.bartlett": {"en": "Bartlett's χ²", "ua": "χ² Бартлетта"},
    "efa.row.df": {"en": "df", "ua": "df"},
    "efa.kmo.marvelous": {"en": "marvelous", "ua": "чудовий"},
    "efa.kmo.meritorious": {"en": "meritorious", "ua": "гідний"},
    "efa.kmo.middling": {"en": "middling", "ua": "посередній"},
    "efa.kmo.mediocre": {"en": "mediocre", "ua": "задовільний"},
    "efa.kmo.miserable": {"en": "miserable", "ua": "низький"},
    "efa.kmo.unacceptable": {"en": "unacceptable", "ua": "неприйнятний"},
    "efa.report.kmo": {
        "en": "Sampling adequacy is {label} (KMO = {kmo}). ",
        "ua": "Адекватність вибірки {label} (KMO = {kmo}). ",
    },
    "efa.report.bartlett_sig": {
        "en": "Bartlett's test of sphericity is significant (χ²({df}) = {chi2}, {p}), so the variables are sufficiently correlated for factoring. ",
        "ua": "Тест сферичності Бартлетта значущий (χ²({df}) = {chi2}, {p}), тож змінні достатньо корельовані для факторизації. ",
    },
    "efa.report.bartlett_ns": {
        "en": "Bartlett's test of sphericity is not significant (χ²({df}) = {chi2}, {p}); the variables may be too weakly correlated for factoring. ",
        "ua": "Тест сферичності Бартлетта незначущий (χ²({df}) = {chi2}, {p}); змінні можуть бути надто слабко корельовані для факторизації. ",
    },
    "efa.report.kaiser": {
        "en": "The Kaiser criterion (eigenvalue > 1) suggests {n} factor(s). ",
        "ua": "Критерій Кайзера (власне значення > 1) пропонує {n} фактор(ів). ",
    },
    "efa.report.kaiser_none": {
        "en": "No eigenvalue exceeds 1; consider a scree plot or parallel analysis to choose the number of factors. ",
        "ua": "Жодне власне значення не перевищує 1; для вибору кількості факторів скористайтеся графіком осипу або паралельним аналізом. ",
    },
    "efa.plot.scree": {"en": "Scree plot", "ua": "Графік осипу"},
    "efa.plot.kaiser_line": {
        "en": "Eigenvalue = 1 (Kaiser criterion)",
        "ua": "Власне значення = 1 (критерій Кайзера)",
    },
    "efa.plot.loadings": {"en": "Factor loadings heatmap", "ua": "Теплокарта факторних навантажень"},
    "efa.plot.factors": {"en": "Factors", "ua": "Фактори"},
    "efa.plot.variables": {"en": "Variables", "ua": "Змінні"},
    # ----- Confirmatory Factor Analysis -----
    "cfa.description": {
        "en": (
            "Confirmatory factor analysis (CFA) tests a factor structure you specify &mdash; you "
            "assign the observed variables to each latent factor. The model is fitted by maximum "
            "likelihood and reports model-fit indices (&chi;&sup2;, RMSEA, CFI, TLI, SRMR), the "
            "standardised factor loadings, and (for an oblique model) the factor correlations. "
            "Use the loadings to judge how well each variable measures its assigned factor."
        ),
        "ua": (
            "Конфірматорний факторний аналіз (CFA) перевіряє задану вами факторну структуру "
            "&mdash; ви призначаєте спостережувані змінні кожному латентному фактору. Модель "
            "оцінюється методом максимальної правдоподібності та подає індекси відповідності "
            "(&chi;&sup2;, RMSEA, CFI, TLI, SRMR), стандартизовані факторні навантаження та "
            "(для косокутної моделі) кореляції факторів. За навантаженнями оцінюйте, наскільки "
            "добре змінна вимірює призначений їй фактор."
        ),
    },
    "cfa.error.min_per_factor": {
        "en": "Each factor needs at least two variables (for identification).",
        "ua": "Кожен фактор потребує щонайменше двох змінних (для ідентифікації).",
    },
    "cfa.error.fit_failed": {
        "en": "The CFA model could not be fit: {error}",
        "ua": "Не вдалося оцінити модель CFA: {error}",
    },
    "cfa.caption.fit": {"en": "Model fit indices", "ua": "Індекси відповідності моделі"},
    "cfa.caption.loadings": {"en": "Factor loadings (standardized)", "ua": "Факторні навантаження (стандартизовані)"},
    "cfa.caption.phi": {"en": "Factor correlation matrix (Φ)", "ua": "Матриця кореляцій факторів (Φ)"},
    "cfa.col.index": {"en": "Index", "ua": "Індекс"},
    "cfa.col.value": {"en": "Value", "ua": "Значення"},
    "cfa.col.interpretation": {"en": "Interpretation", "ua": "Інтерпретація"},
    "cfa.col.variable": {"en": "Variable", "ua": "Змінна"},
    "cfa.fit.acceptable": {"en": "acceptable", "ua": "прийнятна"},
    "cfa.fit.mediocre": {"en": "mediocre", "ua": "посередня"},
    "cfa.fit.poor": {"en": "poor", "ua": "погана"},
    "cfa.fit.good": {"en": "good", "ua": "добра"},
    "cfa.fit.excellent": {"en": "excellent", "ua": "відмінна"},
    "cfa.report.chi2_good": {
        "en": "The exact-fit χ² test is non-significant (χ²({df}) = {chi2}, {p}), consistent with good fit. ",
        "ua": "Тест точної відповідності χ² незначущий (χ²({df}) = {chi2}, {p}), що узгоджується з доброю відповідністю. ",
    },
    "cfa.report.chi2_poor": {
        "en": "The exact-fit χ² test is significant (χ²({df}) = {chi2}, {p}), indicating some misfit &mdash; though χ² is sensitive to sample size. ",
        "ua": "Тест точної відповідності χ² значущий (χ²({df}) = {chi2}, {p}), що вказує на певну невідповідність &mdash; хоча χ² чутливий до обсягу вибірки. ",
    },
    "cfa.report.indices": {
        "en": "RMSEA = {rmsea} ({rmsea_label}); CFI = {cfi} ({cfi_label}); TLI = {tli} ({tli_label}); SRMR = {srmr} ({srmr_label}). ",
        "ua": "RMSEA = {rmsea} ({rmsea_label}); CFI = {cfi} ({cfi_label}); TLI = {tli} ({tli_label}); SRMR = {srmr} ({srmr_label}). ",
    },
    "cfa.report.not_converged": {
        "en": "Warning: the optimiser did not fully converge, so the solution may be unreliable. ",
        "ua": "Увага: оптимізатор не повністю збігся, тож розв'язок може бути ненадійним. ",
    },
    "cfa.loadings_sig_note": {
        "en": "* p &lt; .05, ** p &lt; .01, *** p &lt; .001 (Wald test of each loading).",
        "ua": "* p &lt; .05, ** p &lt; .01, *** p &lt; .001 (тест Вальда для кожного навантаження).",
    },
    "cfa.plot.loadings": {"en": "Factor loadings heatmap", "ua": "Теплокарта факторних навантажень"},
    "cfa.plot.factors": {"en": "Factors", "ua": "Фактори"},
    "cfa.plot.variables": {"en": "Variables", "ua": "Змінні"},
    # ----- Cluster analysis -----
    "cluster.caption.assignments": {
        "en": "Cluster Assignments",
        "ua": "Призначення кластерів",
    },
    "cluster.caption.centroids": {
        "en": "Cluster Centroids",
        "ua": "Центроїди кластерів",
    },
    "cluster.col.observation": {
        "en": "Observation",
        "ua": "Спостереження",
    },
    "cluster.col.cluster": {
        "en": "Cluster",
        "ua": "Кластер",
    },
    "cluster.msg.select_variable": {
        "en": "Select at least one variable.",
        "ua": "Оберіть щонайменше одну змінну.",
    },
    "cluster.msg.not_enough": {
        "en": "Not enough data for {n} clusters.",
        "ua": "Недостатньо даних для {n} кластерів.",
    },
    "cluster.msg.method_not_implemented": {
        "en": "Selected clustering method not implemented.",
        "ua": "Обраний метод кластеризації не реалізовано.",
    },
    "cluster.header": {
        "en": "Method: <i>{method}</i>; Clusters: <i>{n}</i>",
        "ua": "Метод: <i>{method}</i>; Кластерів: <i>{n}</i>",
    },
    "cluster.description": {
        "en": (
            "Cluster analysis groups observations so that those within a cluster are more "
            "similar to each other than to those in other clusters. K-means partitions the data "
            "into a chosen number of clusters by minimising the within-cluster sum of squares. "
            "The module reports the cluster sizes, the cluster centroids (in the original units), "
            "a silhouette quality score, and a 2-D scatter of the clusters."
        ),
        "ua": (
            "Кластерний аналіз групує спостереження так, щоб усередині кластера вони були "
            "подібнішими між собою, ніж до спостережень з інших кластерів. K-середніх розбиває "
            "дані на задану кількість кластерів, мінімізуючи внутрішньокластерну суму квадратів. "
            "Модуль подає розміри кластерів, центроїди (в оригінальних одиницях), оцінку якості "
            "(силует) та двовимірну діаграму розсіювання кластерів."
        ),
    },
    "cluster.caption.summary": {"en": "Cluster summary", "ua": "Зведення кластерів"},
    "cluster.caption.quality": {"en": "Cluster quality", "ua": "Якість кластеризації"},
    "cluster.col.size": {"en": "Size", "ua": "Розмір"},
    "cluster.col.percent": {"en": "%", "ua": "%"},
    "cluster.col.metric": {"en": "Metric", "ua": "Показник"},
    "cluster.col.value": {"en": "Value", "ua": "Значення"},
    "cluster.col.interpretation": {"en": "Interpretation", "ua": "Інтерпретація"},
    "cluster.metric.silhouette": {"en": "Mean silhouette", "ua": "Середній силует"},
    "cluster.metric.inertia": {"en": "Within-cluster SS (inertia)", "ua": "Внутрішньокластерна сума квадратів"},
    "cluster.sil.strong": {"en": "strong structure", "ua": "сильна структура"},
    "cluster.sil.reasonable": {"en": "reasonable structure", "ua": "помірна структура"},
    "cluster.sil.weak": {"en": "weak structure", "ua": "слабка структура"},
    "cluster.sil.none": {"en": "no substantial structure", "ua": "немає суттєвої структури"},
    "cluster.report.summary": {
        "en": "K-means formed {k} clusters (sizes: {sizes}). ",
        "ua": "K-середніх утворив {k} кластерів (розміри: {sizes}). ",
    },
    "cluster.report.silhouette": {
        "en": "The mean silhouette is {sil} ({label}). ",
        "ua": "Середній силует дорівнює {sil} ({label}). ",
    },
    "cluster.report.standardized": {
        "en": "Variables were standardised (z-scored) before clustering. ",
        "ua": "Перед кластеризацією змінні стандартизовано (z-оцінки). ",
    },
    "cluster.report.unstandardized": {
        "en": "Variables were clustered on their original scale. ",
        "ua": "Кластеризацію виконано в оригінальному масштабі змінних. ",
    },
    "cluster.plot.scatter": {"en": "Cluster scatter plot", "ua": "Діаграма розсіювання кластерів"},
    "cluster.plot.kselect_sil": {
        "en": "Silhouette by number of clusters",
        "ua": "Силует за кількістю кластерів",
    },
    "cluster.plot.kselect_inertia": {
        "en": "Inertia by number of clusters (elbow)",
        "ua": "Інерція за кількістю кластерів (лікоть)",
    },
    "cluster.plot.k": {"en": "Number of clusters (k)", "ua": "Кількість кластерів (k)"},
    "cluster.plot.dendrogram": {"en": "Dendrogram", "ua": "Дендрограма"},
    "cluster.plot.distance": {"en": "Distance", "ua": "Відстань"},
    "cluster.plot.observations": {"en": "Observations", "ua": "Спостереження"},
    "cluster.plot.cluster_label": {"en": "Cluster {n}", "ua": "Кластер {n}"},
    "cluster.plot.pc": {"en": "PC{n} ({pct}%)", "ua": "ГК{n} ({pct}%)"},
    # ----- Correlation -----
    "correlation.name.pearson": {
        "en": "Pearson correlation coefficient",
        "ua": "коефіцієнт кореляції Пірсона",
    },
    "correlation.name.spearman": {
        "en": "Spearman rank correlation coefficient",
        "ua": "коефіцієнт рангової кореляції Спірмена",
    },
    "correlation.name.kendall": {
        "en": "Kendall rank correlation coefficient",
        "ua": "коефіцієнт рангової кореляції Кендалла",
    },
    "correlation.name.kendall_c": {
        "en": "Kendall τ<sub>c</sub> rank correlation coefficient",
        "ua": "коефіцієнт рангової кореляції Кендалла τ<sub>c</sub>",
    },
    "correlation.name.phi": {
        "en": "Phi binary correlation coefficient",
        "ua": "коефіцієнт бінарної кореляції φ (фі)",
    },
    "correlation.name.tetrachoric": {
        "en": "Tetrachoric binary correlation coefficient",
        "ua": "тетрахоричний коефіцієнт кореляції",
    },
    "correlation.name.polychoric": {
        "en": "Polychoric ordinal correlation coefficient",
        "ua": "поліхоричний коефіцієнт кореляції",
    },
    "correlation.strength.strong": {"en": "strong", "ua": "сильну"},
    "correlation.strength.moderate": {"en": "moderate", "ua": "помірну"},
    "correlation.strength.weak": {"en": "weak", "ua": "слабку"},
    "correlation.strength.very_weak": {"en": "very weak", "ua": "дуже слабку"},
    "effect.col.magnitude": {"en": "Magnitude", "ua": "Величина"},
    "verbal.significant": {"en": "significant", "ua": "значущий"},
    "verbal.not_significant": {"en": "not significant", "ua": "незначущий"},
    "verbal.yes": {"en": "yes", "ua": "так"},
    "verbal.no": {"en": "no", "ua": "ні"},
    "verbal.col_significant": {"en": "Significant?", "ua": "Значущість?"},
    "verbal.col_equal_var": {"en": "Equal var.?", "ua": "Рівні дисп.?"},
    "effect.magnitude.negligible": {"en": "negligible", "ua": "незначна"},
    "effect.magnitude.small": {"en": "small", "ua": "мала"},
    "effect.magnitude.medium": {"en": "medium", "ua": "середня"},
    "effect.magnitude.large": {"en": "large", "ua": "велика"},
    "correlation.sign.positive": {"en": "positive", "ua": "позитивну"},
    "correlation.sign.negative": {"en": "negative", "ua": "негативну"},
    "correlation.report.intro": {
        "en": "A {name} was calculated to assess the relationship between the variables {vars}. ",
        "ua": "Розраховано {name} для оцінки зв'язку між змінними {vars}. ",
    },
    "correlation.report.two_significant": {
        "en": "There was a {strength} {sign} correlation between the two variables, {stats}. ",
        "ua": "Виявлено {strength} {sign} кореляцію між двома змінними, {stats}. ",
    },
    "correlation.report.two_nonsignificant": {
        "en": "The relationship between the two variables was not significant, {stats}. ",
        "ua": "Зв'язок між двома змінними статистично незначущий, {stats}. ",
    },
    "correlation.report.multi_significant": {
        "en": "There was a {strength} {sign} correlation between '{var1}' and '{var2}', {stats}. ",
        "ua": "Виявлено {strength} {sign} кореляцію між «{var1}» та «{var2}», {stats}. ",
    },
    "correlation.report.multi_nonsignificant": {
        "en": "The correlation between '{var1}' and '{var2}' was not significant, {stats}. ",
        "ua": "Кореляція між «{var1}» та «{var2}» статистично незначуща, {stats}. ",
    },
    "correlation.report.negligible": {
        "en": "Although statistically significant, the relationship is negligible. ",
        "ua": "Попри статистичну значущість, зв'язок є незначним за величиною. ",
    },
    "correlation.report.none_significant": {
        "en": "No significant correlations were found between the selected variables.",
        "ua": "Статистично значущих кореляцій між обраними змінними не виявлено.",
    },
    "correlation.partial.note": {
        "en": "<b>Partial correlations</b>, controlling for {controls}. ",
        "ua": "<b>Часткові кореляції</b>, з контролем за {controls}. ",
    },
    "correlation.partial.method_error": {
        "en": "Partial correlation supports only Pearson or Spearman; pick one of those as the correlation type.",
        "ua": "Часткова кореляція підтримує лише Пірсона або Спірмена; оберіть один із цих типів кореляції.",
    },
    "correlation.warning.ordinal_pearson": {
        "en": "Warning: Ordinal data detected. Pearson correlation is not suitable for ordinal data.",
        "ua": "Увага: виявлено порядкові дані. Кореляція Пірсона не підходить для порядкових даних.",
    },
    "correlation.plot.matrix_title": {
        "en": "Correlation Matrix",
        "ua": "Матриця кореляцій",
    },
    "correlation.plot.scatter_tab": {
        "en": "Plot: {a} vs {b}",
        "ua": "Графік: {a} проти {b}",
    },
    "correlation.plot.scatter_title": {
        "en": "Correlation between {a} and {b}",
        "ua": "Кореляція між {a} та {b}",
    },
    "correlation.plot.points": {"en": "Data points", "ua": "Спостереження"},
    "correlation.plot.regression_line": {"en": "Linear regression", "ua": "Лінійна регресія"},
    "correlation.plot.band": {"en": "Standard error", "ua": "Стандартна похибка"},
    "correlation.table.caption": {
        "en": "{name} between {vars}.",
        "ua": "{name} між {vars}.",
    },
    "correlation.table.significance_note": {
        "en": "* p &lt; .05; ** p &lt; .01; *** p &lt; .001",
        "ua": "* p &lt; .05; ** p &lt; .01; *** p &lt; .001",
    },
    "correlation.table.name.pearson": {"en": "Pearson's r", "ua": "r Пірсона"},
    "correlation.table.name.spearman": {"en": "Spearman's r", "ua": "r Спірмена"},
    "correlation.table.name.kendall": {"en": "Kendall's τ", "ua": "τ Кендалла"},
    "correlation.table.name.kendall_c": {
        "en": "Kendall's τ<sub>c</sub>",
        "ua": "τ<sub>c</sub> Кендалла",
    },
    "correlation.table.name.phi": {"en": "Phi φ", "ua": "φ (фі)"},
    "correlation.table.name.tetrachoric": {
        "en": "Tetrachoric ρ<sub>t</sub>",
        "ua": "тетрахоричний ρ<sub>t</sub>",
    },
    "correlation.table.name.polychoric": {
        "en": "Polychoric ρ<sub>pc</sub>",
        "ua": "поліхоричний ρ<sub>pc</sub>",
    },
    "correlation.error.min_variables": {
        "en": "Please select at least two variables to correlate.",
        "ua": "Будь ласка, оберіть щонайменше дві змінні для кореляції.",
    },
    "correlation.description": {
        "en": (
            "<h2>Correlation</h2>"
            "<h3>Description</h3>"
            "<div>Estimates the strength and direction of association between the selected "
            "variables and reports a correlation matrix (with significance), an optional "
            "verbal summary, a heatmap, and pairwise scatter plots with regression lines.</div>"
            "<div>Choose the correlation coefficient that matches your data:"
            "<ul>"
            "<li>Pearson's r &ndash; linear association between continuous variables.</li>"
            "<li>Spearman's ρ / Kendall's τ &ndash; monotonic (rank) association for ordinal "
            "data; Kendall is preferred for small samples or many ties.</li>"
            "<li>Phi φ &ndash; association between two binary variables.</li>"
            "<li>Tetrachoric / Polychoric &ndash; association between binary / ordinal "
            "variables assumed to reflect underlying continuous variables.</li>"
            "</ul></div>"
        ),
        "ua": (
            "<h2>Кореляція</h2>"
            "<h3>Опис</h3>"
            "<div>Оцінює силу та напрямок зв'язку між обраними змінними та виводить "
            "кореляційну матрицю (зі значущістю), необов'язковий словесний підсумок, теплову "
            "карту та парні діаграми розсіювання з лініями регресії.</div>"
            "<div>Оберіть коефіцієнт кореляції відповідно до ваших даних:"
            "<ul>"
            "<li>r Пірсона &ndash; лінійний зв'язок між неперервними змінними.</li>"
            "<li>ρ Спірмена / τ Кендалла &ndash; монотонний (ранговий) зв'язок для порядкових "
            "даних; Кендалл краще підходить для малих вибірок або багатьох зв'язків.</li>"
            "<li>φ (фі) &ndash; зв'язок між двома бінарними змінними.</li>"
            "<li>Тетрахоричний / поліхоричний &ndash; зв'язок між бінарними / порядковими "
            "змінними, що відображають приховані неперервні змінні.</li>"
            "</ul></div>"
        ),
    },
    # ----- Descriptive statistics -----
    "descriptive.error.no_variables": {
        "en": "Please select at least one variable.",
        "ua": "Будь ласка, оберіть щонайменше одну змінну.",
    },
    "descriptive.table.caption": {
        "en": "Descriptive statistics",
        "ua": "Описова статистика",
    },
    "descriptive.freq.caption": {
        "en": "Frequencies: {col}",
        "ua": "Частоти: {col}",
    },
    "descriptive.freq.category": {"en": "Category", "ua": "Категорія"},
    "descriptive.freq.count": {"en": "Count", "ua": "Кількість"},
    "descriptive.freq.percent": {"en": "%", "ua": "%"},
    "descriptive.freq.total": {"en": "Total", "ua": "Загалом"},
    "descriptive.freq.group_line": {
        "en": "In {group} (n = {n}), the most common {col} was “{category}” ({pct}%). ",
        "ua": "У групі {group} (n = {n}) найпоширеніше значення «{col}» — «{category}» ({pct}%). ",
    },
    "descriptive.normality.caption": {
        "en": "Normality test ({test})",
        "ua": "Перевірка нормальності ({test})",
    },
    "descriptive.normality.col_normal": {"en": "Normal?", "ua": "Нормальний?"},
    "descriptive.normality.yes": {"en": "Yes", "ua": "Так"},
    "descriptive.normality.no": {"en": "No", "ua": "Ні"},
    "descriptive.normality.intro": {
        "en": "A {test} test of normality was conducted. ",
        "ua": "Проведено перевірку нормальності за критерієм {test}. ",
    },
    "descriptive.normality.normal": {
        "en": "{var} was normally distributed ({stats}). ",
        "ua": "{var} має нормальний розподіл ({stats}). ",
    },
    "descriptive.normality.not_normal": {
        "en": "{var} was not normally distributed ({stats}). ",
        "ua": "{var} не має нормального розподілу ({stats}). ",
    },
    "descriptive.outliers.line": {
        "en": "Analysis of {target} identified {n} outlier(s): {items}. ",
        "ua": "Аналіз «{target}» виявив {n} викид(ів): {items}. ",
    },
    "descriptive.outliers.id_list": {
        "en": "All outlier IDs: ({ids}). ",
        "ua": "Усі ID викидів: ({ids}). ",
    },
    "descriptive.density": {"en": "Density", "ua": "Щільність"},
    "descriptive.plot.distribution": {
        "en": "Distribution of {col}",
        "ua": "Розподіл «{col}»",
    },
    "descriptive.plot.box": {
        "en": "Box plot of {col}",
        "ua": "Діаграма розмаху «{col}»",
    },
    "descriptive.plot.qq": {
        "en": "Normal Q-Q plot of {col}",
        "ua": "Графік Q-Q (нормальний) «{col}»",
    },
    "descriptive.plot.frequency": {
        "en": "Frequencies of {col}",
        "ua": "Частоти «{col}»",
    },
    "descriptive.plot.pie": {
        "en": "Composition of {col}",
        "ua": "Склад «{col}»",
    },
    "descriptive.qq.theoretical": {
        "en": "Theoretical quantiles",
        "ua": "Теоретичні квантилі",
    },
    "descriptive.qq.sample": {
        "en": "Sample quantiles",
        "ua": "Вибіркові квантилі",
    },
    "descriptive.description": {
        "en": (
            "<h2>Descriptive Statistics</h2>"
            "<h3>Description</h3>"
            "<div>Summarises the selected variables. Numeric variables get a summary table "
            "(N, missing, mean, SD, min, max, Shapiro&ndash;Wilk; optionally median, IQR, "
            "SE, skewness and kurtosis); categorical variables get frequency tables.</div>"
            "<div>Optional plots (each opt-in): distribution histograms with a KDE curve, "
            "box plots with outliers, normal Q-Q plots, and &mdash; for categorical "
            "variables &mdash; frequency bar charts and pie charts. A grouping column "
            "splits the numeric summary, distributions and box plots by group.</div>"
            "<div>For distributions you can set the histogram bin width (1 for Likert "
            "scales) and the KDE smoothing.</div>"
        ),
        "ua": (
            "<h2>Описова статистика</h2>"
            "<h3>Опис</h3>"
            "<div>Підсумовує обрані змінні. Для числових змінних будується підсумкова "
            "таблиця (N, пропуски, середнє, SD, мінімум, максимум, Шапіро&ndash;Вілк; за "
            "бажанням медіана, IQR, SE, асиметрія та ексцес); для категоріальних &mdash; "
            "таблиці частот.</div>"
            "<div>Додаткові графіки (кожен вмикається окремо): гістограми розподілу з "
            "кривою KDE, діаграми розмаху з викидами, графіки Q-Q, а для категоріальних "
            "змінних &mdash; стовпчасті діаграми частот і кругові діаграми. Стовпець "
            "групування розбиває підсумок, розподіли та діаграми розмаху за групами.</div>"
            "<div>Для розподілів можна задати ширину інтервалу гістограми (1 для шкал "
            "Лайкерта) та згладжування KDE.</div>"
        ),
    },
}


def t(key: str, **kwargs) -> str:
    """Return the template for ``key`` in the active language (English fallback),
    formatted with ``kwargs``."""
    entry = TRANSLATIONS[key]
    template = entry.get(LANGUAGE.language.value, entry["en"])
    return template.format(**kwargs)
