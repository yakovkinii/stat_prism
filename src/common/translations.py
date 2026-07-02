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
    "common.ci_95": {
        "en": "95% CI",
        "ua": "95% ДІ",
    },
    "common.column_numbering.legend": {
        "en": "Columns: {items}.",
        "ua": "Стовпці: {items}.",
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
    "common.configure_hint_refresh": {
        "en": "Please refresh this result or change any setting on a panel on the right.",
        "ua": "Будь ласка, оновіть цей результат або змініть будь-яке налаштування на панелі праворуч.",
    },
    "common.msg.select_id": {
        "en": "Select the ID column.",
        "ua": "Оберіть колонку з ідентифікатором.",
    },
    # ----- Contingency -----
    "contingency.table_caption": {
        "en": "Contingency Table",
        "ua": "Таблиця сполученості",
    },
    "contingency.total": {
        "en": "Total",
        "ua": "Загалом",
    },
    "contingency.chi2_caption": {
        "en": "Chi-square Test",
        "ua": "Хі-квадрат тест",
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
    "contingency.mcnemar.caption": {
        "en": "Paired-data symmetry test",
        "ua": "Тест симетрії для парних даних",
    },
    "contingency.mcnemar.name": {
        "en": "McNemar test",
        "ua": "тест Мак-Немара",
    },
    "contingency.mcnemar.name_bowker": {
        "en": "Bowker test of symmetry",
        "ua": "тест симетрії Боукера",
    },
    "contingency.mcnemar.not_square": {
        "en": (
            "The symmetry test needs a square table with matching categories on both axes "
            "(the same items measured twice). The selected variables do not form one."
        ),
        "ua": (
            "Тест симетрії потребує квадратної таблиці з однаковими категоріями по обох осях "
            "(ті самі об'єкти, виміряні двічі). Обрані змінні її не утворюють."
        ),
    },
    "contingency.mcnemar.significant": {
        "en": "The {name} indicates a significant change between the paired measurements ({stats}).",
        "ua": "{name} вказує на значущу зміну між парними вимірами ({stats}).",
    },
    "contingency.mcnemar.not_significant": {
        "en": "The {name} does not indicate a significant change between the paired measurements ({stats}).",
        "ua": "{name} не вказує на значущу зміну між парними вимірами ({stats}).",
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
        "en": "Distribution",
        "ua": "Розподіл",
    },
    "contingency.plot_y_axis": {
        "en": "{col} (%)",
        "ua": "{col} (%)",
    },
    "contingency.fisher_caption": {
        "en": "Fisher's Exact Test",
        "ua": "Точний тест Фішера",
    },
    "contingency.fisher_text": {
        "en": "Fisher's exact test: odds ratio = {odds}, {p}.",
        "ua": "Точний тест Фішера: відношення шансів = {odds}, {p}.",
    },
    "contingency.pct_caption": {
        "en": "Percentages ({col1} × {col2})",
        "ua": "Відсотки ({col1} × {col2})",
    },
    "contingency.pct_note_row": {
        "en": "Row percentages: each cell as a percentage of its row total.",
        "ua": "Відсотки за рядком: кожна клітинка як відсоток від суми рядка.",
    },
    "contingency.pct_note_column": {
        "en": "Column percentages: each cell as a percentage of its column total.",
        "ua": "Відсотки за стовпцем: кожна клітинка як відсоток від суми стовпця.",
    },
    "contingency.pct_note_total": {
        "en": "Total percentages: each cell as a percentage of the grand total.",
        "ua": "Відсотки від загальної суми: кожна клітинка як відсоток від загальної суми.",
    },
    "contingency.residuals.caption": {
        "en": "Post-hoc: adjusted standardized residuals ({col1} × {col2})",
        "ua": "Пост-хок: скориговані стандартизовані залишки ({col1} × {col2})",
    },
    "contingency.residuals.note": {
        "en": (
            "Adjusted standardized residuals; |z| &gt; {z} (in bold) marks cells that "
            "depart from independence at p &lt; .05 (two-tailed)."
        ),
        "ua": (
            "Скориговані стандартизовані залишки; |z| &gt; {z} (жирним) позначає клітинки, "
            "що відхиляються від незалежності при p &lt; .05 (двобічний)."
        ),
    },
    "contingency.residuals.not_significant": {
        "en": "Post-hoc residuals were requested but the overall test is not significant, so they are omitted.",
        "ua": "Пост-хок залишки було запитано, але загальний тест незначущий, тому їх не показано.",
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
    "ttest.ci_sentence": {
        "en": "95% confidence intervals for Cohen's d: {items}.",
        "ua": "95% довірчі інтервали для d Коена: {items}.",
    },
    "ttest.posthoc_sentence": {
        "en": (
            "The {name} post-hoc test for {col} has revealed a significant "
            "difference between the following groups: {groups}."
        ),
        "ua": (
            "Апостеріорний тест {name} для «{col}» виявив статистично значущу " "різницю між такими групами: {groups}."
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
    # ----- Paired / Repeated Measures -----
    "paired.error.min_conditions": {
        "en": "Select at least two conditions (repeated measurements) to compare.",
        "ua": "Виберіть щонайменше дві умови (повторні вимірювання) для порівняння.",
    },
    "paired.error.insufficient": {
        "en": "Too few complete cases after dropping rows with missing values (found {n}, at least 3 required).",
        "ua": "Замало повних спостережень після вилучення рядків із пропусками (знайдено {n}, потрібно щонайменше 3).",
    },
    "paired.error.auto_no_assumptions": {
        "en": (
            "Assumption checks are off and the method is Automatic, so the appropriate test "
            "cannot be determined. Choose a method or enable assumption checks."
        ),
        "ua": (
            "Перевірку припущень вимкнено, а метод — «Визначити автоматично», тому неможливо "
            "обрати відповідний тест. Оберіть метод або увімкніть перевірку припущень."
        ),
    },
    "paired.caption.descriptives": {
        "en": "Descriptive statistics",
        "ua": "Описова статистика",
    },
    "paired.col.condition": {
        "en": "Condition",
        "ua": "Умова",
    },
    "paired.col.n": {
        "en": "N",
        "ua": "N",
    },
    "paired.col.normal": {
        "en": "Normal?",
        "ua": "Нормальний?",
    },
    "paired.caption.normality": {
        "en": "Assumption checks",
        "ua": "Перевірка припущень",
    },
    "paired.row.differences": {
        "en": "Differences",
        "ua": "Різниці",
    },
    "paired.row.sphericity": {
        "en": "Sphericity (Mauchly)",
        "ua": "Сферичність (Маучлі)",
    },
    "paired.caption.paired_t": {
        "en": "Paired-samples t-test",
        "ua": "t-критерій для залежних вибірок",
    },
    "paired.caption.wilcoxon": {
        "en": "Wilcoxon signed-rank test",
        "ua": "Критерій знакових рангів Вілкоксона",
    },
    "paired.caption.rm_anova": {
        "en": "Repeated-measures ANOVA",
        "ua": "Дисперсійний аналіз з повторними вимірюваннями",
    },
    "paired.caption.friedman": {
        "en": "Friedman test",
        "ua": "Критерій Фрідмана",
    },
    "paired.test.paired_t": {
        "en": "paired-samples t-test",
        "ua": "t-критерій для залежних вибірок",
    },
    "paired.test.wilcoxon": {
        "en": "Wilcoxon signed-rank test",
        "ua": "критерій знакових рангів Вілкоксона",
    },
    "paired.test.rm_anova": {
        "en": "repeated-measures ANOVA",
        "ua": "дисперсійний аналіз з повторними вимірюваннями",
    },
    "paired.test.friedman": {
        "en": "Friedman test",
        "ua": "критерій Фрідмана",
    },
    "paired.note.gg": {
        "en": "Greenhouse–Geisser corrected p {p}, ε = {eps}.",
        "ua": "Поправка Грінхауса–Гайссера: p {p}, ε = {eps}.",
    },
    "paired.caption.posthoc_param": {
        "en": "Pairwise comparisons (paired t, Holm-adjusted)",
        "ua": "Попарні порівняння (залежний t, поправка Холма)",
    },
    "paired.caption.posthoc_nonparam": {
        "en": "Pairwise comparisons (Nemenyi)",
        "ua": "Попарні порівняння (Немені)",
    },
    "paired.posthoc.pairwise_t": {
        "en": "pairwise paired t",
        "ua": "попарний залежний t",
    },
    "paired.posthoc.nemenyi": {
        "en": "Nemenyi",
        "ua": "Немені",
    },
    "paired.posthoc_sentence": {
        "en": "The {name} post-hoc test revealed a significant difference between the following conditions: {groups}.",
        "ua": "Апостеріорний тест {name} виявив статистично значущу різницю між такими умовами: {groups}.",
    },
    "paired.verbal.result": {
        "en": "{test} — the difference between conditions is {conclusion} ({stats}).",
        "ua": "{test} — різниця між умовами {conclusion} ({stats}).",
    },
    "paired.plot.value_axis": {
        "en": "Value",
        "ua": "Значення",
    },
    "paired.plot.condition_axis": {
        "en": "Condition",
        "ua": "Умова",
    },
    "paired.description": {
        "en": (
            "<h2>Paired / Repeated Measures</h2>"
            "<h3>Description</h3>"
            "<div>Compare two or more repeated measurements taken on the same respondents "
            "(e.g. before / after, or several time points or conditions) to determine whether "
            "they differ significantly.</div>"
            "<div>With two conditions the paired-samples family is used:"
            "<ul>"
            "<li>If the paired differences are normally distributed (Shapiro-Wilk), the "
            "paired-samples t-test is used.</li>"
            "<li>Otherwise, the Wilcoxon signed-rank test is used.</li>"
            "</ul></div>"
            "<div>With three or more conditions the repeated-measures family is used:"
            "<ul>"
            "<li>If every condition is normally distributed (Shapiro-Wilk), repeated-measures "
            "ANOVA is used (with the Greenhouse-Geisser correction reported).</li>"
            "<li>Otherwise, the Friedman test is used.</li>"
            "</ul></div>"
            "<h3>Inputs</h3>"
            "<div><b>Conditions:</b><br>Two or more columns holding the repeated measurements "
            "of the same respondents. Respondents missing any condition are dropped.</div>"
        ),
        "ua": (
            "<h2>Залежні вибірки / повторні вимірювання</h2>"
            "<h3>Опис</h3>"
            "<div>Порівняння двох або більше повторних вимірювань на тих самих респондентах "
            "(наприклад, до / після або кілька моментів часу чи умов) для визначення, чи "
            "відрізняються вони статистично значущо.</div>"
            "<div>За двох умов використовується родина для залежних вибірок:"
            "<ul>"
            "<li>Якщо різниці пар розподілені нормально (критерій Шапіро–Уілка), "
            "використовується t-критерій для залежних вибірок.</li>"
            "<li>Інакше використовується критерій знакових рангів Вілкоксона.</li>"
            "</ul></div>"
            "<div>За трьох і більше умов використовується родина повторних вимірювань:"
            "<ul>"
            "<li>Якщо кожна умова розподілена нормально (критерій Шапіро–Уілка), "
            "використовується ANOVA з повторними вимірюваннями (з поправкою "
            "Грінхауса–Гайссера).</li>"
            "<li>Інакше використовується критерій Фрідмана.</li>"
            "</ul></div>"
            "<h3>Вхідні дані</h3>"
            "<div><b>Умови:</b><br>Два або більше стовпців із повторними вимірюваннями тих "
            "самих респондентів. Респонденти, у яких пропущена будь-яка умова, вилучаються.</div>"
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
    "reliability.col.omega_deleted": {"en": "&omega; if removed", "ua": "&omega; за вилучення"},
    "reliability.col.interpretation": {"en": "Interpretation", "ua": "Інтерпретація"},
    "reliability.col.improves": {"en": "Improves &alpha;?", "ua": "Покращує &alpha;?"},
    "reliability.col.alpha_improves": {"en": "Improves &alpha;?", "ua": "Покращує &alpha;?"},
    "reliability.col.omega_improves": {"en": "Improves &omega;?", "ua": "Покращує &omega;?"},
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
        "en": "Regression",
        "ua": "Регресія",
    },
    "regression.plot.data": {"en": "Data points", "ua": "Спостереження"},
    "regression.plot.line": {"en": "Regression line", "ua": "Лінія регресії"},
    "regression.plot.identity": {"en": "Perfect fit", "ua": "Ідеальна відповідність"},
    "regression.plot.obs_pred_title": {
        "en": "Observed vs. predicted {dv}",
        "ua": "Спостережені та передбачені {dv}",
    },
    "regression.plot.predicted": {"en": "Predicted", "ua": "Передбачені"},
    "regression.plot.observed": {"en": "Observed", "ua": "Спостережені"},
    "regression.plot.line_sd": {
        "en": "Regression line ({sd} SD)",
        "ua": "Лінія регресії ({sd} SD)",
    },
    "regression.plot.direct": {
        "en": "Direct effect (corrected for mediation)",
        "ua": "Прямий ефект (з поправкою на медіацію)",
    },
    "regression.plot.total": {"en": "Total effect", "ua": "Загальний ефект"},
    "regression.plot.mediation_title": {"en": "Mediation paths: {dv}", "ua": "Шляхи медіації: {dv}"},
    "regression.plot.band": {"en": "Standard error", "ua": "Стандартна похибка"},
    "regression.diag.vif_caption": {"en": "Multicollinearity (VIF)", "ua": "Мультиколінеарність (VIF)"},
    "regression.diag.influence_caption": {"en": "Influential observations", "ua": "Впливові спостереження"},
    "regression.diag.observation": {"en": "Observation", "ua": "Спостереження"},
    "regression.diag.mahalanobis": {"en": "Mahalanobis D", "ua": "D Махаланобіса"},
    "regression.diag.cooks": {"en": "Cook's D", "ua": "D Кука"},
    "regression.diag.leverage": {"en": "Leverage", "ua": "Розмах (leverage)"},
    "regression.diag.std_resid": {"en": "Std. residual", "ua": "Станд. залишок"},
    "regression.report.influence_some": {
        "en": (
            "{n} observation(s) are flagged as potentially influential "
            "(Cook's D > {cooks}, leverage > {leverage}, or |std. residual| > 3). "
            "Inspect them before trusting the fit. "
        ),
        "ua": (
            "Позначено {n} потенційно впливових спостережень "
            "(D Кука > {cooks}, leverage > {leverage} або |станд. залишок| > 3). "
            "Перевірте їх, перш ніж довіряти моделі. "
        ),
    },
    "regression.report.influence_none": {
        "en": "No observations exceed the usual influence thresholds. ",
        "ua": "Жодне спостереження не перевищує звичайних порогів впливовості. ",
    },
    "regression.report.durbin_watson": {
        "en": (
            "Durbin-Watson = {dw} (≈ 2 suggests independent residuals; "
            "much below 2 indicates positive autocorrelation, above 2 negative)."
        ),
        "ua": (
            "Дарбін-Уотсон = {dw} (≈ 2 свідчить про незалежність залишків; "
            "значно менше 2 — додатна автокореляція, більше 2 — від'ємна)."
        ),
    },
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
    # ----- Regression: logistic (binary outcome) -----
    "regression.error.not_binary": {
        "en": "Logistic regression needs a binary dependent variable (exactly two distinct values; found {values}).",
        "ua": "Логістична регресія потребує бінарної залежної змінної (рівно два різні значення; знайдено {values}).",
    },
    "regression.error.logit_no_mediation": {
        "en": "Mediation is not supported for logistic regression. Remove the mediator variable.",
        "ua": "Медіація не підтримується для логістичної регресії. Вилучіть змінну-медіатор.",
    },
    "regression.error.not_multinomial": {
        "en": "Multinomial regression needs a dependent variable with at least three categories (found {values}).",
        "ua": "Мультиноміальна регресія потребує залежної змінної щонайменше з трьома категоріями (знайдено {values}).",
    },
    "regression.multinom.vs_base": {
        "en": "{cat} vs {base} (reference)",
        "ua": "{cat} проти {base} (еталон)",
    },
    "regression.report.multinom_fit": {
        "en": (
            "A multinomial logistic regression modelled {dv} (reference category: {base}). The "
            "model is a {pseudo} (McFadden pseudo R²) improvement over the null, χ²({df}) = "
            "{chi2}, p {p}, and is "
        ),
        "ua": (
            "Мультиноміальна логістична регресія моделювала {dv} (еталонна категорія: {base}). "
            "Модель покращує нульову на {pseudo} (псевдо R² Макфаддена), χ²({df}) = {chi2}, "
            "p {p}, і є "
        ),
    },
    "regression.report.multinom_intro": {
        "en": "Coefficients compare each category of {dv} against the reference «{base}» on the log-odds scale. ",
        "ua": "Коефіцієнти порівнюють кожну категорію {dv} з еталоном «{base}» у шкалі лог-шансів. ",
    },
    "regression.report.multinom_cat": {
        "en": "For {cat} vs {base}: {items}.",
        "ua": "Для {cat} проти {base}: {items}.",
    },
    "regression.error.moderator_and_mediator": {
        "en": (
            "Choose either a moderator or a mediator, not both — moderated mediation is not "
            "supported. Remove one of them."
        ),
        "ua": (
            "Оберіть або модератор, або медіатор, але не обидва — модерована медіація не "
            "підтримується. Вилучіть одну зі змінних."
        ),
    },
    "regression.col.pseudo_r2": {"en": "Pseudo R<sup>2</sup>", "ua": "Псевдо R<sup>2</sup>"},
    "regression.col.z": {"en": "z", "ua": "z"},
    "regression.col.odds_ratio": {"en": "OR", "ua": "ВШ"},
    "regression.dir.increase": {"en": "increases the odds", "ua": "підвищує шанси"},
    "regression.dir.decrease": {"en": "decreases the odds", "ua": "знижує шанси"},
    "regression.report.logit_fit": {
        "en": (
            "A logistic regression modelled the odds of {dv} = {positive}. The model is a "
            "{pseudo} (McFadden pseudo R²) improvement over the null, χ²({df}) = {chi2}, "
            "p {p}, and is "
        ),
        "ua": (
            "Логістична регресія моделювала шанси {dv} = {positive}. Модель покращує нульову "
            "на {pseudo} (псевдо R² Макфаддена), χ²({df}) = {chi2}, p {p}, і є "
        ),
    },
    "regression.report.logit_coef_intro": {
        "en": (
            "The coefficients are on the log-odds scale; the odds ratio (OR) is exp(B) &mdash; "
            "the multiplicative change in the odds of {dv} = {positive} per one-unit increase in "
            "the predictor (OR &gt; 1 raises the odds, &lt; 1 lowers them). "
        ),
        "ua": (
            "Коефіцієнти подано в шкалі логарифма шансів; відношення шансів (ВШ) — це exp(B), "
            "мультиплікативна зміна шансів {dv} = {positive} на одиницю зростання предиктора "
            "(ВШ &gt; 1 підвищує шанси, &lt; 1 знижує). "
        ),
    },
    "regression.report.logit_coef_sig": {
        "en": "Significant predictors of {positive}: {items}.",
        "ua": "Значущі предиктори {positive}: {items}.",
    },
    "regression.plot.prob_curve": {"en": "Fitted probability", "ua": "Прогнозована ймовірність"},
    "regression.plot.prob_axis": {
        "en": "P({positive})",
        "ua": "P({positive})",
    },
    "regression.plot.logit_title": {
        "en": "Probability of {dv} = {positive} by {iv}",
        "ua": "Ймовірність {dv} = {positive} залежно від {iv}",
    },
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
    "efa.error.polychoric_failed": {
        "en": "The polychoric correlation matrix could not be estimated for these items. Try Pearson.",
        "ua": "Не вдалося оцінити поліхоричну кореляційну матрицю для цих пунктів. Спробуйте Пірсона.",
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
    "efa.kmo.meritorious": {"en": "good", "ua": "добрий"},
    "efa.kmo.middling": {"en": "above average", "ua": "вище середнього"},
    "efa.kmo.mediocre": {"en": "below average", "ua": "нижче середнього"},
    "efa.kmo.miserable": {"en": "bad", "ua": "поганий"},
    "efa.kmo.unacceptable": {"en": "unacceptable", "ua": "неприйнятний"},
    "efa.report.kmo": {
        "en": "Sampling adequacy is {label} (KMO = {kmo}). ",
        "ua": "Адекватність вибірки {label} (KMO = {kmo}). ",
    },
    "efa.report.bartlett_sig": {
        "en": "Bartlett's test of sphericity is significant (χ²({df}) = {chi2}, {p}), "
        "so the variables are sufficiently correlated for factoring. ",
        "ua": "Тест сферичності Бартлетта значущий (χ²({df}) = {chi2}, {p}), "
        "тож змінні достатньо корельовані для факторизації. ",
    },
    "efa.report.bartlett_ns": {
        "en": "Bartlett's test of sphericity is not significant (χ²({df}) = {chi2}, {p}); "
        "the variables may be too weakly correlated for factoring. ",
        "ua": "Тест сферичності Бартлетта незначущий (χ²({df}) = {chi2}, {p}); "
        "змінні можуть бути надто слабко корельовані для факторизації. ",
    },
    "efa.report.kaiser": {
        "en": "The Kaiser criterion (eigenvalue > 1) suggests {n} factor(s). ",
        "ua": "Критерій Кайзера (власне значення > 1) пропонує {n} фактор(ів). ",
    },
    "efa.report.kaiser_none": {
        "en": "No eigenvalue exceeds 1; consider a scree plot or parallel analysis to choose "
        "the number of factors. ",
        "ua": "Жодне власне значення не перевищує 1; для вибору кількості факторів скористайтеся "
        "графіком осипу або паралельним аналізом. ",
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
    "cfa.caption.mod_hints": {
        "en": "Modification hints (possible cross-loadings)",
        "ua": "Підказки щодо модифікації (можливі крос-навантаження)",
    },
    "cfa.caption.second_order": {"en": "Second-order factor loadings", "ua": "Навантаження фактора другого порядку"},
    "cfa.col.first_order": {"en": "First-order factor", "ua": "Фактор першого порядку"},
    "cfa.col.loading": {"en": "Loading", "ua": "Навантаження"},
    "cfa.mod_hints_need_factors": {
        "en": "Cross-loading hints need at least two factors with residual information.",
        "ua": "Підказки щодо крос-навантажень потребують щонайменше двох факторів із інформацією про залишки.",
    },
    "cfa.mod_hints_none": {
        "en": "No cross-loadings suggested — every residual correlation with another factor is below {threshold}.",
        "ua": "Крос-навантажень не запропоновано — усі залишкові кореляції з іншими факторами нижчі за {threshold}.",
    },
    "cfa.col.suggested_factor": {"en": "Suggested factor", "ua": "Пропонований фактор"},
    "cfa.col.resid_score": {"en": "Mean |resid.|", "ua": "Сер. |залишок|"},
    "cfa.mod_hints_note": {
        "en": (
            "Residual-based suggestion (mean absolute standardized residual with the factor's "
            "items), not an exact modification index. High values hint a cross-loading may improve fit."
        ),
        "ua": (
            "Підказка на основі залишків (середній абсолютний стандартизований залишок з пунктами "
            "фактора), а не точний індекс модифікації. Високі значення натякають, що крос-навантаження "
            "може покращити відповідність."
        ),
    },
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
        "ua": "Тест точної відповідності χ² незначущий (χ²({df}) = {chi2}, {p}), "
        "що узгоджується з доброю відповідністю. ",
    },
    "cfa.report.chi2_poor": {
        "en": "The exact-fit χ² test is significant (χ²({df}) = {chi2}, {p}), "
        "indicating some misfit &mdash; though χ² is sensitive to sample size. ",
        "ua": "Тест точної відповідності χ² значущий (χ²({df}) = {chi2}, {p}), "
        "що вказує на певну невідповідність &mdash; хоча χ² чутливий до обсягу вибірки. ",
    },
    "cfa.report.indices": {
        "en": "RMSEA = {rmsea} ({rmsea_label}); CFI = {cfi} ({cfi_label}); "
        "TLI = {tli} ({tli_label}); SRMR = {srmr} ({srmr_label}). ",
        "ua": "RMSEA = {rmsea} ({rmsea_label}); CFI = {cfi} ({cfi_label}); "
        "TLI = {tli} ({tli_label}); SRMR = {srmr} ({srmr_label}). ",
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
    "cfa.plot.structure": {"en": "Factor structure", "ua": "Факторна структура"},
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
    "correlation.report.cross_intro": {
        "en": "A {name} was calculated between the first variable set ({rows}) and the second set ({cols}). ",
        "ua": "Розраховано {name} між першим набором змінних ({rows}) та другим набором ({cols}). ",
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
    "correlation.warning.constant_column": {
        "en": "Note: {columns} has no variance (a single value), " "so its correlations are undefined and left blank.",
        "ua": "Нотатка: {columns} не має варіації (одне значення), "
        "тому його кореляції невизначені й залишені порожніми.",
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
        "en": "Correlation",
        "ua": "Кореляція",
    },
    "correlation.plot.points": {"en": "Data points", "ua": "Спостереження"},
    "correlation.plot.regression_line": {"en": "Linear regression", "ua": "Лінійна регресія"},
    "correlation.plot.band": {"en": "Standard error", "ua": "Стандартна похибка"},
    "correlation.table.caption": {
        "en": "{name}",
        "ua": "{name}",
    },
    "correlation.table.cross_caption": {
        "en": "{name}",
        "ua": "{name}",
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
    "correlation.error.cross_min": {
        "en": "For a two-set (cross) correlation, select at least one variable in each set.",
        "ua": "Для крос-кореляції двох наборів оберіть щонайменше одну змінну в кожному наборі.",
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
            "<h3>Inputs</h3>"
            "<div><b>Variables:</b> the variable set to correlate (a square matrix of every "
            "pair).</div>"
            "<div><b>Control for (partial, optional):</b> covariates to partial out (Pearson or "
            "Spearman only).</div>"
            "<div><b>Second variable set (cross, optional):</b> when given, a rectangular "
            "two-set matrix is produced instead &mdash; every variable in the first set against "
            "every variable in the second set (rows × columns), rather than a square matrix.</div>"
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
            "<h3>Вхідні дані</h3>"
            "<div><b>Змінні:</b> набір змінних для кореляції (квадратна матриця всіх пар).</div>"
            "<div><b>Контроль (часткова, необов'язково):</b> коваріати для виключення впливу "
            "(лише Пірсон або Спірмен).</div>"
            "<div><b>Другий набір змінних (крос, необов'язково):</b> якщо задано, будується "
            "прямокутна матриця двох наборів &mdash; кожна змінна першого набору проти кожної "
            "змінної другого (рядки × стовпці) замість квадратної матриці.</div>"
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
    "descriptive.normality.note_blank": {
        "en": "Blank cells: the test could not run " "(needs at least 3 non-missing values with variation).",
        "ua": "Порожні клітинки: критерій не вдалося обчислити "
        "(потрібно щонайменше 3 непропущені значення з варіацією).",
    },
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
    # ----- Methodology fine-print (rendered smaller, under each module's description) -----
    "correlation.fine_print": {
        "en": (
            "<b>Methodology &amp; assumptions</b>"
            "<ul>"
            "<li><b>Coefficients &amp; p-values.</b>"
            "<ul>"
            "<li>Pearson&rsquo;s r &mdash; t-distribution p-value, df = n &minus; 2 (reported).</li>"
            "<li>Spearman&rsquo;s &rho; / Kendall&rsquo;s &tau; (tau-b) / &tau;<sub>c</sub> &mdash; "
            "p-values from SciPy; no df is reported.</li>"
            "<li>Phi &phi; &mdash; &radic;(&chi;<sup>2</sup>/N) from the 2&times;2 table; p-value from "
            "the chi-square test.</li>"
            "<li>Tetrachoric &mdash; maximum-likelihood estimate for a 2&times;2 table; Wald p-value "
            "(z = &rho;/SE), df = n &minus; 2. Returned blank when the pair is not 2&times;2.</li>"
            "<li>Polychoric &mdash; maximum-likelihood estimate; likelihood-ratio p-value (df = 1).</li>"
            "</ul></li>"
            "<li><b>Confidence intervals.</b> When enabled, a 95% CI is shown via the Fisher "
            "<i>z</i> transform (SE = 1/&radic;(n &minus; 3)) for Pearson&rsquo;s r, and for "
            "Spearman&rsquo;s &rho; with a small variance inflation (SE &times; 1.03). A CI is "
            "<i>not</i> defensible for Kendall&rsquo;s &tau;, phi, tetrachoric or polychoric, so "
            "those cells show &lsquo;&mdash;&rsquo;.</li>"
            "<li><b>Partial correlation.</b> If any &lsquo;Control for&rsquo; variables are given, the "
            "table shows <i>partial</i> correlations among the selected variables with the linear "
            "effect of the controls removed from both sides of each pair (Pearson or Spearman only; "
            "df = n &minus; 2 &minus; number of controls). Pairwise scatter plots are omitted in this "
            "mode, since the raw scatter would not reflect the partialled relationship.</li>"
            "<li><b>Two-set (cross) correlation.</b> If a &lsquo;Second variable set&rsquo; is given, "
            "a rectangular matrix is produced instead of the square one: every variable in the first "
            "set (rows) against every variable in the second set (columns), with all cells filled. It "
            "honours the same coefficient choice, the partial-correlation controls, the heatmap and "
            "the pairwise plots; a variable paired with itself (when it appears in both sets) is "
            "skipped in the verbal summary.</li>"
            "<li><b>Missing data.</b> Pairwise deletion &mdash; each pair uses only rows where both "
            "variables are present.</li>"
            "<li><b>Ordinal variables.</b> Selected ordinal variables are mapped to numeric codes. "
            "Using Pearson&rsquo;s r on ordinal data triggers a warning (it assumes interval data).</li>"
            "<li><b>Reporting.</b> Significance stars: * p &lt; .05, ** p &lt; .01, *** p &lt; .001; "
            "the verbal summary uses &alpha; = .05. Strength of |r|: &gt; .5 strong, &gt; .3 moderate, "
            "&gt; .1 weak, otherwise very weak. All tests are two-sided.</li>"
            "<li><b>Numbered columns.</b> &lsquo;Number columns in tables&rsquo; replaces the variable "
            "names in the tables with numbers (1, 2, 3&hellip;) and adds a numbered legend to each "
            "table&rsquo;s note; the verbal summary keeps the real names.</li>"
            "</ul>"
        ),
        "ua": (
            "<b>Методологія та припущення</b>"
            "<ul>"
            "<li><b>Коефіцієнти та p-значення.</b>"
            "<ul>"
            "<li>r Пірсона &mdash; p-значення за t-розподілом, df = n &minus; 2 (наводиться).</li>"
            "<li>&rho; Спірмена / &tau; Кендала (tau-b) / &tau;<sub>c</sub> &mdash; "
            "p-значення зі SciPy; df не наводиться.</li>"
            "<li>Фі &phi; &mdash; &radic;(&chi;<sup>2</sup>/N) із таблиці 2&times;2; p-значення з "
            "тесту хі-квадрат.</li>"
            "<li>Тетрахорична &mdash; оцінка максимальної правдоподібності для таблиці 2&times;2; "
            "p-значення Вальда (z = &rho;/SE), df = n &minus; 2. Порожнє, якщо пара не 2&times;2.</li>"
            "<li>Поліхорична &mdash; оцінка максимальної правдоподібності; p-значення відношення "
            "правдоподібностей (df = 1).</li>"
            "</ul></li>"
            "<li><b>Довірчі інтервали.</b> Якщо увімкнено, 95% ДІ обчислюється через z-перетворення "
            "Фішера (SE = 1/&radic;(n &minus; 3)) для r Пірсона та для &rho; Спірмена з невеликим "
            "збільшенням дисперсії (SE &times; 1.03). ДІ <i>не</i> є обґрунтованим для &tau; Кендала, "
            "фі, тетрахоричної чи поліхоричної кореляції, тож ці комірки показують "
            "&lsquo;&mdash;&rsquo;.</li>"
            "<li><b>Часткова кореляція.</b> Якщо задано змінні в полі &lsquo;Контролювати&rsquo;, "
            "таблиця показує <i>часткові</i> кореляції між обраними змінними з усуненням лінійного "
            "впливу контрольних змінних з обох боків кожної пари (лише Пірсон або Спірмен; "
            "df = n &minus; 2 &minus; кількість контрольних). У цьому режимі попарні діаграми "
            "розсіювання не будуються, оскільки сире розсіювання не відображало б часткового "
            "зв&rsquo;язку.</li>"
            "<li><b>Двонаборова (перехресна) кореляція.</b> Якщо задано &lsquo;Другий набір "
            "змінних&rsquo;, замість квадратної матриці будується прямокутна: кожна змінна першого "
            "набору (рядки) проти кожної змінної другого набору (стовпці), з усіма заповненими "
            "комірками. Враховуються той самий вибір коефіцієнта, контрольні змінні часткової "
            "кореляції, теплова карта та попарні діаграми; пару змінної самої з собою (якщо вона є "
            "в обох наборах) у словесному підсумку пропущено.</li>"
            "<li><b>Пропущені дані.</b> Попарне вилучення &mdash; кожна пара використовує лише "
            "рядки, де присутні обидві змінні.</li>"
            "<li><b>Порядкові змінні.</b> Обрані порядкові змінні відображаються на числові коди. "
            "Застосування r Пірсона до порядкових даних спричиняє попередження (він припускає "
            "інтервальні дані).</li>"
            "<li><b>Звітування.</b> Зірочки значущості: * p &lt; .05, ** p &lt; .01, *** p &lt; .001; "
            "словесний підсумок використовує &alpha; = .05. Сила |r|: &gt; .5 сильна, &gt; .3 помірна, "
            "&gt; .1 слабка, інакше дуже слабка. Усі тести двосторонні.</li>"
            "<li><b>Нумерація стовпців.</b> &lsquo;Нумерувати стовпці в таблицях&rsquo; замінює назви "
            "змінних у таблицях номерами (1, 2, 3&hellip;) і додає нумеровану легенду до примітки "
            "кожної таблиці; словесний підсумок зберігає справжні назви.</li>"
            "</ul>"
        ),
    },
    "mean_comparison.fine_print": {
        "en": (
            "<b>Methodology &amp; assumptions</b>"
            "<ul>"
            "<li><b>Test selection.</b> Two groups use the t-test family; three or more use the "
            "ANOVA family. Numeric variables that pass the assumption checks use parametric tests; "
            "ordinal / non-numeric variables and numeric variables that fail normality use "
            "non-parametric tests.</li>"
            "<li><b>Normality.</b> Shapiro&ndash;Wilk, computed per group. A variable is treated as "
            "normal only when every group passes (p &gt; .05).</li>"
            "<li><b>Homogeneity of variance.</b> Levene&rsquo;s test centred on the <i>mean</i> "
            "(not the median / Brown&ndash;Forsythe variant). Equal variances are assumed when "
            "p &gt; .05.</li>"
            "<li><b>Parametric, 2 groups.</b> Equal variances &rarr; Student&rsquo;s independent "
            "t-test (pooled SD); unequal variances &rarr; Welch&rsquo;s t-test with "
            "Welch&ndash;Satterthwaite degrees of freedom.</li>"
            "<li><b>Parametric, 3+ groups.</b> Equal variances &rarr; one-way ANOVA; unequal "
            "variances &rarr; Welch&rsquo;s ANOVA.</li>"
            "<li><b>Non-parametric.</b> Two groups &rarr; Mann&ndash;Whitney U; three or more "
            "&rarr; Kruskal&ndash;Wallis H.</li>"
            "<li><b>Effect sizes.</b>"
            "<ul>"
            "<li>Student&rsquo;s t: Cohen&rsquo;s d using the pooled SD.</li>"
            "<li>Welch&rsquo;s t: Cohen&rsquo;s d standardised by the root-mean of the two group "
            "variances, &radic;((s<sub>1</sub><sup>2</sup>+s<sub>2</sub><sup>2</sup>)/2), rather "
            "than the pooled SD.</li>"
            "<li>Mann&ndash;Whitney: rank-biserial correlation "
            "r = 1 &minus; 2&middot;U<sub>1</sub>/(n<sub>1</sub>&middot;n<sub>2</sub>), reported "
            "<i>with its sign</i> so the direction of the effect is preserved; the U printed in the "
            "table is the smaller of U<sub>1</sub>/U<sub>2</sub>.</li>"
            "<li>ANOVA family: one-way ANOVA reports &eta;&sup2; = (df<sub>b</sub>&middot;F) / "
            "(df<sub>b</sub>&middot;F + df<sub>w</sub>); Welch&rsquo;s ANOVA reports partial "
            "&eta;&sup2;<sub>p</sub> (from pingouin). Magnitude bands: .01 small, .06 medium, "
            ".14 large (Cohen). The &ldquo;Effect size / Post-hoc&rdquo; switch controls both this "
            "column and the post-hoc tests.</li>"
            "</ul></li>"
            "<li><b>Confidence intervals.</b> When enabled, a 95% CI for Cohen&rsquo;s d is shown "
            "from its large-sample standard error, "
            "SE = &radic;((n<sub>1</sub>+n<sub>2</sub>)/(n<sub>1</sub>n<sub>2</sub>) + "
            "d<sup>2</sup>/(2(n<sub>1</sub>+n<sub>2</sub>))). This is the parametric (t-test) "
            "effect size only; the Mann&ndash;Whitney rank-biserial r is shown without a CI.</li>"
            "<li><b>Verbal indicators.</b> &lsquo;Verbal indicators in tables&rsquo; adds plain-language "
            "columns next to each p-value: a Significant? conclusion on the result tables and a "
            "Normal? / Equal var.? conclusion on the assumption-check tables (all at &alpha; = .05). "
            "Where an effect size is shown it also adds a Magnitude column: Cohen&rsquo;s d as "
            "negligible / small / medium / large (|d| 0.2 / 0.5 / 0.8); the rank-biserial r by the "
            "correlation bands (|r| .1 / .3 / .5). Post-hoc p-value matrices are left unannotated.</li>"
            "<li><b>Post-hoc</b> (only when enabled and the omnibus test is significant): one-way "
            "ANOVA &rarr; Tukey HSD; Welch&rsquo;s ANOVA &rarr; Tamhane&rsquo;s T2; "
            "Kruskal&ndash;Wallis &rarr; Dunn&rsquo;s test.</li>"
            "<li><b>Threshold.</b> All tests are two-sided and use &alpha; = .05.</li>"
            "<li><b>Missing data.</b> Missing values are dropped per variable before each test; "
            "missing group labels follow the &ldquo;Missing in grouping&rdquo; setting.</li>"
            "<li><b>Numbered variables.</b> &lsquo;Number variables in tables&rsquo; replaces the "
            "variable names in the result tables with numbers (1, 2, 3&hellip;) and adds a numbered "
            "legend to each table&rsquo;s note; the verbal summary keeps the real names.</li>"
            "</ul>"
        ),
        "ua": (
            "<b>Методологія та припущення</b>"
            "<ul>"
            "<li><b>Вибір тесту.</b> Дві групи &mdash; родина t-тестів; три і більше &mdash; "
            "родина ANOVA. Числові змінні, що проходять перевірку припущень, використовують "
            "параметричні тести; порядкові / нечислові змінні та числові змінні, що не проходять "
            "перевірку на нормальність, використовують непараметричні тести.</li>"
            "<li><b>Нормальність.</b> Шапіро&ndash;Вілк, обчислюється для кожної групи. Змінна "
            "вважається нормальною лише тоді, коли кожна група проходить перевірку (p &gt; .05).</li>"
            "<li><b>Однорідність дисперсій.</b> Тест Левена, центрований за <i>середнім</i> "
            "(не за медіаною / варіант Брауна&ndash;Форсайта). Рівність дисперсій припускається, "
            "коли p &gt; .05.</li>"
            "<li><b>Параметричний, 2 групи.</b> Рівні дисперсії &rarr; незалежний t-тест "
            "Стьюдента (об&rsquo;єднане SD); нерівні дисперсії &rarr; t-тест Велча зі ступенями "
            "свободи Велча&ndash;Саттертвейта.</li>"
            "<li><b>Параметричний, 3+ груп.</b> Рівні дисперсії &rarr; однофакторний ANOVA; "
            "нерівні дисперсії &rarr; ANOVA Велча.</li>"
            "<li><b>Непараметричний.</b> Дві групи &rarr; U Манна&ndash;Вітні; три і більше "
            "&rarr; H Краскела&ndash;Волліса.</li>"
            "<li><b>Розміри ефекту.</b>"
            "<ul>"
            "<li>t Стьюдента: d Коена з об&rsquo;єднаним SD.</li>"
            "<li>t Велча: d Коена, стандартизований за середньоквадратичним двох групових "
            "дисперсій, &radic;((s<sub>1</sub><sup>2</sup>+s<sub>2</sub><sup>2</sup>)/2), а не за "
            "об&rsquo;єднаним SD.</li>"
            "<li>Манн&ndash;Вітні: рангово-бісеріальна кореляція "
            "r = 1 &minus; 2&middot;U<sub>1</sub>/(n<sub>1</sub>&middot;n<sub>2</sub>), наводиться "
            "<i>зі своїм знаком</i>, щоб зберегти напрям ефекту; U у таблиці &mdash; це менше з "
            "U<sub>1</sub>/U<sub>2</sub>.</li>"
            "<li>Родина ANOVA: однофакторний ANOVA наводить &eta;&sup2; = (df<sub>b</sub>&middot;F) / "
            "(df<sub>b</sub>&middot;F + df<sub>w</sub>); ANOVA Велча наводить часткове "
            "&eta;&sup2;<sub>p</sub> (з pingouin). Смуги величини: .01 малий, .06 середній, "
            ".14 великий (Коен). Перемикач &ldquo;Розмір ефекту / Апостеріорні&rdquo; керує і цим "
            "стовпцем, і апостеріорними тестами.</li>"
            "</ul></li>"
            "<li><b>Довірчі інтервали.</b> Якщо увімкнено, 95% ДІ для d Коена обчислюється з його "
            "великовибіркової стандартної похибки "
            "SE = &radic;((n<sub>1</sub>+n<sub>2</sub>)/(n<sub>1</sub>n<sub>2</sub>) + "
            "d<sup>2</sup>/(2(n<sub>1</sub>+n<sub>2</sub>))). Це стосується лише параметричного "
            "(t-тест) розміру ефекту; рангово-бісеріальний r Манна&ndash;Вітні наводиться без ДІ.</li>"
            "<li><b>Словесні індикатори.</b> &lsquo;Словесні індикатори в таблицях&rsquo; додають "
            "стовпці звичайною мовою поруч із кожним p-значенням: висновок Значущо? у таблицях "
            "результатів і висновок Нормально? / Рівні дисп.? у таблицях перевірки припущень "
            "(усі при &alpha; = .05). Де показано розмір ефекту, додається стовпець Величина: "
            "d Коена як незначний / малий / середній / великий (|d| 0.2 / 0.5 / 0.8); "
            "рангово-бісеріальний r за смугами кореляції (|r| .1 / .3 / .5). Матриці p-значень "
            "апостеріорних тестів залишаються без анотацій.</li>"
            "<li><b>Апостеріорні</b> (лише коли увімкнено та омнібусний тест значущий): "
            "однофакторний ANOVA &rarr; HSD Тьюкі; ANOVA Велча &rarr; T2 Тамхейна; "
            "Краскел&ndash;Волліс &rarr; тест Данна.</li>"
            "<li><b>Поріг.</b> Усі тести двосторонні та використовують &alpha; = .05.</li>"
            "<li><b>Пропущені дані.</b> Пропущені значення вилучаються для кожної змінної перед "
            "кожним тестом; пропущені мітки груп підпорядковуються налаштуванню "
            "&ldquo;Пропущені у групуванні&rdquo;.</li>"
            "<li><b>Нумерація змінних.</b> &lsquo;Нумерувати змінні в таблицях&rsquo; замінює назви "
            "змінних у таблицях результатів номерами (1, 2, 3&hellip;) і додає нумеровану легенду до "
            "примітки кожної таблиці; словесний підсумок зберігає справжні назви.</li>"
            "</ul>"
        ),
    },
    "reliability.fine_print": {
        "en": (
            "<b>Methodology &amp; assumptions</b>"
            "<ul>"
            "<li><b>Coefficients.</b> Cronbach&rsquo;s &alpha; from the item correlation matrix "
            "(standardised &alpha;): &alpha; = k/(k&minus;1) &middot; (1 &minus; tr(R)/&Sigma;R), where k "
            "is the number of items and R the item correlation matrix. Optionally <b>McDonald&rsquo;s "
            "&omega;</b> (omega-total) from a single common-factor fit: &omega; = (&Sigma;&lambda;)&sup2; "
            "/ [(&Sigma;&lambda;)&sup2; + &Sigma;&psi;], with loadings &lambda; and residual variances "
            "&psi;. &omega; relaxes &alpha;&rsquo;s equal-loadings (tau-equivalence) assumption and is "
            "often the better choice for congeneric scales.</li>"
            "<li><b>Correlation type.</b> The same estimators as the Correlation analysis. Pearson, "
            "Spearman, Kendall&rsquo;s &tau;-b and Kendall&rsquo;s &tau;-c work on the items directly; "
            "Polychoric assumes an underlying continuous variable behind each ordinal item. Phi and "
            "Tetrachoric require binary items (&le; 2 unique values) and are rescaled to 0&ndash;1 "
            "first; Tetrachoric assumes an underlying continuous variable. (For ordinal Likert-type "
            "items, Polychoric is generally preferred over Pearson.)</li>"
            "<li><b>If item removed.</b> Each item&rsquo;s &lsquo;&alpha; if removed&rsquo; is &alpha; "
            "recomputed on the remaining items. The corrected item&ndash;total (item&ndash;rest) "
            "correlation is computed from the same item correlation matrix as &alpha; &mdash; "
            "r<sub>i</sub> = (&Sigma; of the item&rsquo;s off-diagonal correlations) / "
            "&radic;(variance of the rest-sum) with standardised items &mdash; rather than from the "
            "raw scores, so it stays consistent with the chosen correlation type (this is what "
            "psych::alpha reports when given a correlation matrix, and is the correct form for "
            "Phi / Tetrachoric / Polychoric). An item whose removal raises &alpha; may be weakening "
            "the scale.</li>"
            "<li><b>Interpretation.</b> &alpha; &gt; .9 excellent, &gt; .8 good, &gt; .7 acceptable, "
            "&gt; .6 questionable, &gt; .5 poor, otherwise unacceptable. &alpha; reflects only the "
            "correlation among items, not whether they belong together in content &mdash; that "
            "remains the researcher&rsquo;s judgement.</li>"
            "<li><b>Verbal indicators.</b> &lsquo;Verbal indicators in tables&rsquo; adds plain-language "
            "columns: the interpretation band next to &alpha;, and an &lsquo;Improves &alpha;?&rsquo; "
            "yes/no on the item table (yes = removing that item would raise &alpha;).</li>"
            "<li><b>Caveat.</b> Cronbach&rsquo;s &alpha; assumes the items are unidimensional and "
            "roughly tau-equivalent (equal true-score contributions); when that does not hold it can "
            "under- or over-state reliability, and McDonald&rsquo;s &omega; may be preferable. &alpha; "
            "also tends to rise simply with more items.</li>"
            "<li><b>Missing data.</b> Correlations are computed pairwise on the available values.</li>"
            "<li><b>Numbered items.</b> &lsquo;Number items in tables&rsquo; replaces the item names in "
            "the item table with numbers (1, 2, 3&hellip;) and adds a numbered legend to the "
            "table&rsquo;s note.</li>"
            "</ul>"
        ),
        "ua": (
            "<b>Методологія та припущення</b>"
            "<ul>"
            "<li><b>Коефіцієнти.</b> &alpha; Кронбаха з кореляційної матриці пунктів "
            "(стандартизована &alpha;): &alpha; = k/(k&minus;1) &middot; (1 &minus; tr(R)/&Sigma;R), де k "
            "&mdash; кількість пунктів, а R &mdash; кореляційна матриця пунктів. За бажанням "
            "<b>&omega; Макдональда</b> (omega-total) з підгонки однієї спільної факторної моделі: "
            "&omega; = (&Sigma;&lambda;)&sup2; / [(&Sigma;&lambda;)&sup2; + &Sigma;&psi;], з "
            "навантаженнями &lambda; та залишковими дисперсіями &psi;. &omega; послаблює припущення "
            "&alpha; про рівні навантаження (тау-еквівалентність) і часто є кращим вибором для "
            "конгенеричних шкал.</li>"
            "<li><b>Тип кореляції.</b> Ті самі оцінювачі, що й в аналізі Кореляції. Пірсон, "
            "Спірмен, &tau;-b Кендала та &tau;-c Кендала працюють із пунктами безпосередньо; "
            "Поліхорична припускає прихований неперервний показник за кожним порядковим пунктом. "
            "Фі та Тетрахорична потребують бінарних пунктів (&le; 2 унікальних значень) і спершу "
            "масштабуються до 0&ndash;1; Тетрахорична припускає прихований неперервний показник. "
            "(Для порядкових пунктів типу Лайкерта Поліхорична зазвичай переважає над Пірсоном.)</li>"
            "<li><b>Якщо пункт вилучено.</b> &lsquo;&alpha; за вилучення&rsquo; кожного пункту &mdash; "
            "це &alpha;, переобчислена на решті пунктів. Виправлена кореляція пункт&ndash;сума "
            "(пункт&ndash;решта) обчислюється з тієї самої кореляційної матриці пунктів, що й &alpha; "
            "&mdash; r<sub>i</sub> = (&Sigma; позадіагональних кореляцій пункту) / "
            "&radic;(дисперсія суми решти) зі стандартизованими пунктами &mdash; а не із сирих "
            "балів, тож вона лишається узгодженою з обраним типом кореляції (саме це наводить "
            "psych::alpha, коли йому передано кореляційну матрицю, і це коректна форма для "
            "Фі / Тетрахоричної / Поліхоричної). Пункт, вилучення якого підвищує &alpha;, можливо, "
            "послаблює шкалу.</li>"
            "<li><b>Інтерпретація.</b> &alpha; &gt; .9 відмінно, &gt; .8 добре, &gt; .7 прийнятно, "
            "&gt; .6 сумнівно, &gt; .5 погано, інакше неприйнятно. &alpha; відображає лише "
            "кореляцію між пунктами, а не те, чи належать вони разом за змістом &mdash; це "
            "лишається судженням дослідника.</li>"
            "<li><b>Словесні індикатори.</b> &lsquo;Словесні індикатори в таблицях&rsquo; додають "
            "стовпці звичайною мовою: смугу інтерпретації поруч із &alpha; та &lsquo;Покращує "
            "&alpha;?&rsquo; так/ні в таблиці пунктів (так = вилучення цього пункту підвищило б "
            "&alpha;).</li>"
            "<li><b>Застереження.</b> &alpha; Кронбаха припускає, що пункти одновимірні та "
            "приблизно тау-еквівалентні (рівний внесок істинного балу); коли це не виконується, "
            "вона може недо- чи переоцінювати надійність, і &omega; Макдональда може бути "
            "кращою. &alpha; також зазвичай зростає просто зі збільшенням кількості пунктів.</li>"
            "<li><b>Пропущені дані.</b> Кореляції обчислюються попарно на наявних значеннях.</li>"
            "<li><b>Нумерація пунктів.</b> &lsquo;Нумерувати пункти в таблицях&rsquo; замінює назви "
            "пунктів у таблиці пунктів номерами (1, 2, 3&hellip;) і додає нумеровану легенду до "
            "примітки таблиці.</li>"
            "</ul>"
        ),
    },
    "regression.fine_print": {
        "en": (
            "<b>Methodology &amp; assumptions</b>"
            "<ul>"
            "<li><b>Estimator.</b> Ordinary least squares (statsmodels OLS) with an intercept. Rows "
            "with any missing value in the used columns are dropped (list-wise).</li>"
            "<li><b>Logistic model.</b> When <b>Model</b> is set to Logistic, a binary logistic "
            "regression (statsmodels Logit) is fitted instead: the dependent variable must have "
            "exactly two distinct values (mapped to 0/1, the larger value being the modelled "
            "&lsquo;positive&rsquo; outcome). The fit table reports McFadden&rsquo;s pseudo R&sup2; "
            "and the likelihood-ratio &chi;&sup2; test; coefficients are log-odds B with the odds "
            "ratio OR = exp(B) and a z statistic. Moderation is supported; mediation, the "
            "standardised &beta; and the residual / Q-Q diagnostics are not (only VIF is shown).</li>"
            "<li><b>Model fit.</b> R&sup2; and adjusted R&sup2;, plus the overall F-test "
            "(F, its two degrees of freedom and p) and the sample size N.</li>"
            "<li><b>Coefficients.</b> Unstandardised B with its standard error (SE), the standardised "
            "coefficient &beta;, the t statistic and its p-value.</li>"
            "<li><b>Table symbols.</b> <b>N</b> sample size (complete rows); <b>R&sup2;</b> share of "
            "the outcome's variance explained; <b>adjusted R&sup2;</b> the same, penalised for the "
            "number of predictors; <b>F</b> the overall model test statistic with degrees of freedom "
            "<b>df</b> = (predictors, residual); <b>B</b> the unstandardised coefficient (expected "
            "change in the outcome per one-unit increase in the predictor, holding the others "
            "constant); <b>SE</b> its standard error; <b>&beta;</b> the standardised coefficient "
            "(B rescaled by SD(predictor)/SD(outcome), so predictors are comparable on a common "
            "scale; blank for the intercept); <b>t</b> = B/SE, the statistic testing the coefficient; "
            "<b>p</b> its two-sided p-value.</li>"
            "<li><b>Significance.</b> A coefficient (or the overall F-test) is &lsquo;significant&rsquo; "
            "when p &lt; .05 &mdash; i.e. the association is unlikely (&lt; 5% under the null) to be "
            "zero in the population, given the other predictors. It speaks to reliability of the sign, "
            "not to the size or practical importance of the effect.</li>"
            "<li><b>Moderation.</b> Adds the moderator and its product with each predictor "
            "(predictor &times; moderator); a significant interaction indicates moderation. The plot "
            "shows simple slopes at &minus;1 SD, mean and +1 SD of the moderator.</li>"
            "<li><b>Mediation.</b> Estimates the predictor&rarr;mediator path and the "
            "predictor/mediator&rarr;outcome paths (a separate Path-estimates table); the plot "
            "contrasts the direct and total effects. Mediation is available for the linear model "
            "only.</li>"
            "<li><b>Supported moderator / mediator combinations.</b> A moderator and a mediator are "
            "<b>mutually exclusive</b> &mdash; this module does not estimate a moderated-mediation "
            "model, so selecting both is rejected with an error. The combinations that run are:"
            "<ul>"
            "<li><b>Linear (OLS):</b> plain regression; with a moderator; or with a mediator.</li>"
            "<li><b>Logistic:</b> plain regression; or with a moderator. A mediator is not supported "
            "and is rejected with an error.</li>"
            "</ul>"
            "In every case the moderator/mediator fields are optional; leaving them empty fits the "
            "plain model.</li>"
            "<li><b>Verbal indicators.</b> &lsquo;Verbal indicators in tables&rsquo; adds a "
            "Significant? column next to each p-value (&alpha; = .05).</li>"
            "<li><b>Diagnostics.</b> Optional. <b>VIF</b> (variance inflation factor) flags "
            "multicollinearity among predictors: &gt; 5 moderate, &gt; 10 high (interaction terms in a "
            "moderation model inflate VIF by construction &mdash; centring the predictors reduces it). "
            "<b>Residuals vs fitted</b> should show a flat, structureless band &mdash; a funnel suggests "
            "heteroscedasticity, a curve suggests non-linearity. The <b>normal Q-Q</b> of residuals "
            "should track the reference line; systematic departures indicate non-normal residuals. "
            "<b>Influential observations</b> are flagged by Cook&rsquo;s D (&gt; 4/n), leverage "
            "(&gt; 2(k+1)/n) or |studentised residual| &gt; 3 (the list is capped at 20 rows). "
            "<b>Durbin&ndash;Watson</b> screens residual autocorrelation: &asymp; 2 suggests "
            "independent residuals, &lt; 1 or &gt; 3 is a concern. Influence and Durbin&ndash;Watson "
            "are reported for the linear model only.</li>"
            "<li><b>Assumptions (not checked here).</b> OLS assumes a roughly linear relationship, "
            "independent and constant-variance (homoscedastic) errors, and &mdash; for exact small-"
            "sample inference &mdash; approximately normal residuals. These are not tested in this "
            "module; inspect residuals / use judgement if in doubt.</li>"
            "<li><b>Threshold.</b> Tests are two-sided and use &alpha; = .05.</li>"
            "</ul>"
        ),
        "ua": (
            "<b>Методологія та припущення</b>"
            "<ul>"
            "<li><b>Оцінювач.</b> Звичайний метод найменших квадратів (statsmodels OLS) з вільним "
            "членом. Рядки з будь-яким пропущеним значенням у використаних стовпцях вилучаються "
            "(списково).</li>"
            "<li><b>Логістична модель.</b> Коли для <b>Моделі</b> обрано Логістичну, натомість "
            "підганяється бінарна логістична регресія (statsmodels Logit): залежна змінна повинна "
            "мати рівно два різні значення (відображаються на 0/1, де більше значення &mdash; це "
            "модельований &lsquo;позитивний&rsquo; результат). Таблиця підгонки наводить псевдо-R&sup2; "
            "Макфаддена та тест відношення правдоподібностей &chi;&sup2;; коефіцієнти &mdash; це "
            "логарифми шансів B з відношенням шансів OR = exp(B) та статистикою z. Модерація "
            "підтримується; медіація, стандартизована &beta; та діагностика залишків / Q-Q &mdash; "
            "ні (показано лише VIF).</li>"
            "<li><b>Якість моделі.</b> R&sup2; та скоригований R&sup2;, а також загальний F-тест "
            "(F, його два ступені свободи та p) і розмір вибірки N.</li>"
            "<li><b>Коефіцієнти.</b> Нестандартизований B з його стандартною похибкою (SE), "
            "стандартизований коефіцієнт &beta;, статистика t та її p-значення.</li>"
            "<li><b>Символи таблиці.</b> <b>N</b> розмір вибірки (повні рядки); <b>R&sup2;</b> частка "
            "поясненої дисперсії результату; <b>скоригований R&sup2;</b> те саме, зі штрафом за "
            "кількість предикторів; <b>F</b> загальна тестова статистика моделі зі ступенями свободи "
            "<b>df</b> = (предиктори, залишок); <b>B</b> нестандартизований коефіцієнт (очікувана "
            "зміна результату на одну одиницю зростання предиктора за сталості інших); <b>SE</b> "
            "його стандартна похибка; <b>&beta;</b> стандартизований коефіцієнт (B, перемасштабований "
            "на SD(предиктор)/SD(результат), тож предиктори зіставні на спільній шкалі; порожній для "
            "вільного члена); <b>t</b> = B/SE, статистика перевірки коефіцієнта; <b>p</b> його "
            "двостороннє p-значення.</li>"
            "<li><b>Значущість.</b> Коефіцієнт (або загальний F-тест) є &lsquo;значущим&rsquo;, "
            "коли p &lt; .05 &mdash; тобто зв&rsquo;язок навряд чи (&lt; 5% за нульової гіпотези) "
            "дорівнює нулю в популяції з огляду на інші предиктори. Це говорить про надійність "
            "знаку, а не про розмір чи практичну важливість ефекту.</li>"
            "<li><b>Модерація.</b> Додає модератор та його добуток із кожним предиктором "
            "(предиктор &times; модератор); значуща взаємодія вказує на модерацію. Графік показує "
            "прості нахили при &minus;1 SD, середньому та +1 SD модератора.</li>"
            "<li><b>Медіація.</b> Оцінює шлях предиктор&rarr;медіатор та шляхи "
            "предиктор/медіатор&rarr;результат (окрема таблиця оцінок шляхів); графік протиставляє "
            "прямий і загальний ефекти. Медіація доступна лише для лінійної моделі.</li>"
            "<li><b>Підтримувані комбінації модератора / медіатора.</b> Модератор і медіатор є "
            "<b>взаємовиключними</b> &mdash; цей модуль не оцінює модель модерованої медіації, тож "
            "вибір обох відхиляється з помилкою. Комбінації, що виконуються:"
            "<ul>"
            "<li><b>Лінійна (OLS):</b> звичайна регресія; з модератором; або з медіатором.</li>"
            "<li><b>Логістична:</b> звичайна регресія; або з модератором. Медіатор не "
            "підтримується і відхиляється з помилкою.</li>"
            "</ul>"
            "У будь-якому разі поля модератора/медіатора необов&rsquo;язкові; залишивши їх "
            "порожніми, підганяється звичайна модель.</li>"
            "<li><b>Словесні індикатори.</b> &lsquo;Словесні індикатори в таблицях&rsquo; додають "
            "стовпець Значущо? поруч із кожним p-значенням (&alpha; = .05).</li>"
            "<li><b>Діагностика.</b> Необов&rsquo;язкова. <b>VIF</b> (фактор інфляції дисперсії) "
            "позначає мультиколінеарність між предикторами: &gt; 5 помірна, &gt; 10 висока (члени "
            "взаємодії в моделі модерації роздувають VIF за побудовою &mdash; центрування "
            "предикторів його зменшує). <b>Залишки проти прогнозованих</b> мають утворювати плоску "
            "безструктурну смугу &mdash; лійка вказує на гетероскедастичність, крива &mdash; на "
            "нелінійність. <b>Нормальний Q-Q</b> залишків має триматися лінії відліку; систематичні "
            "відхилення вказують на ненормальні залишки. <b>Впливові спостереження</b> позначаються "
            "за D Кука (&gt; 4/n), розмахом (leverage &gt; 2(k+1)/n) або |студентизованим залишком| "
            "&gt; 3 (список обмежено 20 рядками). <b>Дарбін&ndash;Вотсон</b> перевіряє автокореляцію "
            "залишків: &asymp; 2 свідчить про незалежні залишки, &lt; 1 або &gt; 3 &mdash; привід для "
            "занепокоєння. Впливові спостереження та Дарбін&ndash;Вотсон наводяться лише для лінійної "
            "моделі.</li>"
            "<li><b>Припущення (тут не перевіряються).</b> OLS припускає приблизно лінійний "
            "зв&rsquo;язок, незалежні похибки зі сталою дисперсією (гомоскедастичні) та &mdash; для "
            "точного висновку на малих вибірках &mdash; приблизно нормальні залишки. У цьому модулі "
            "вони не перевіряються; за сумніву перевірте залишки / скористайтеся судженням.</li>"
            "<li><b>Поріг.</b> Тести двосторонні та використовують &alpha; = .05.</li>"
            "</ul>"
        ),
    },
    "exploratory_factor_analysis.fine_print": {
        "en": (
            "<b>Methodology &amp; assumptions</b>"
            "<ul>"
            "<li><b>Estimation.</b> Common-factor model fitted with factor_analyzer on the variable "
            "correlation matrix (squared multiple correlations as initial communalities). Extraction: "
            "MINRES, Maximum Likelihood, or Principal Axis. Rows with any missing value are dropped "
            "(list-wise) and ordinal items are scored numerically.</li>"
            "<li><b>Sampling adequacy.</b> The Kaiser&ndash;Meyer&ndash;Olkin (KMO) measure (overall "
            "and per-variable MSA) and Bartlett&rsquo;s test of sphericity gauge whether the "
            "correlations support factoring (KMO &gt; .6 and a significant Bartlett test are usually "
            "wanted).</li>"
            "<li><b>Eigenvalues.</b> Eigenvalues of the correlation matrix with the percentage and "
            "cumulative percentage of variance; the scree plot and the Kaiser criterion "
            "(eigenvalue &gt; 1) help choose the number of factors &mdash; a guide, not a rule.</li>"
            "<li><b>Rotation.</b> Orthogonal (Varimax / Quartimax / Equamax / Oblimax) keeps factors "
            "uncorrelated; oblique (Promax / Oblimin / Quartimin) allows correlated factors and adds a "
            "factor-correlation matrix (&Phi;) and a structure matrix. Kaiser normalisation can be "
            "toggled.</li>"
            "<li><b>Loadings.</b> The loadings (pattern) matrix is the direct factor&rarr;variable "
            "effect &mdash; use it to assign variables to factors. Communality is the variance of a "
            "variable explained by the factors; uniqueness is 1 &minus; communality. The structure "
            "matrix (oblique only) is the variable&ndash;factor correlation including shared factor "
            "variance.</li>"
            "<li><b>Out-of-range loadings.</b> A <i>negative</i> loading is normal &mdash; it just means "
            "the variable relates inversely to the factor (a reverse-keyed item); interpret its "
            "magnitude as usual. A loading or communality <i>above 1</i> (equivalently a negative "
            "uniqueness) is a <b>Heywood case</b>: an improper solution. In an oblique <i>pattern</i> "
            "matrix a value slightly above 1 can occur legitimately when factors are strongly "
            "correlated (regression-like weights, not correlations), but a communality &gt; 1 is always "
            "invalid. It usually signals an over-extracted model (too many factors for the data), a "
            "small sample, or near-collinear / duplicate items. Typical fixes: extract fewer factors, "
            "remove redundant items, gather more data, or try a different extraction/rotation.</li>"
            "<li><b>Numbered variables.</b> &lsquo;Number variables in tables&rsquo; replaces the "
            "variable names in the tables (KMO/MSA, loadings, structure) with numbers (1, 2, 3&hellip;) "
            "and adds a numbered legend to each table&rsquo;s note.</li>"
            "</ul>"
        ),
        "ua": (
            "<b>Методологія та припущення</b>"
            "<ul>"
            "<li><b>Оцінювання.</b> Модель спільних факторів, підігнана за допомогою factor_analyzer "
            "на кореляційній матриці змінних (квадрати множинних кореляцій як початкові спільності). "
            "Виділення: MINRES, Максимальна правдоподібність або Головні осі. Рядки з будь-яким "
            "пропущеним значенням вилучаються (списково), а порядкові пункти оцінюються "
            "числово.</li>"
            "<li><b>Адекватність вибірки.</b> Міра Кайзера&ndash;Меєра&ndash;Олкіна (KMO) (загальна "
            "та MSA для кожної змінної) і тест сферичності Бартлетта оцінюють, чи підтримують "
            "кореляції факторизацію (зазвичай бажано KMO &gt; .6 та значущий тест Бартлетта).</li>"
            "<li><b>Власні значення.</b> Власні значення кореляційної матриці з відсотком та "
            "накопиченим відсотком дисперсії; графік осипу та критерій Кайзера (власне "
            "значення &gt; 1) допомагають обрати кількість факторів &mdash; це орієнтир, а не "
            "правило.</li>"
            "<li><b>Обертання.</b> Ортогональне (Varimax / Quartimax / Equamax / Oblimax) лишає "
            "фактори некорельованими; косокутне (Promax / Oblimin / Quartimin) дозволяє корельовані "
            "фактори й додає матрицю кореляцій факторів (&Phi;) та структурну матрицю. Нормалізацію "
            "Кайзера можна перемикати.</li>"
            "<li><b>Навантаження.</b> Матриця навантажень (патерну) &mdash; це прямий ефект "
            "фактор&rarr;змінна; використовуйте її, щоб віднести змінні до факторів. Спільність "
            "&mdash; це дисперсія змінної, пояснена факторами; унікальність &mdash; це 1 &minus; "
            "спільність. Структурна матриця (лише косокутне) &mdash; це кореляція змінна&ndash;фактор "
            "із урахуванням спільної факторної дисперсії.</li>"
            "<li><b>Навантаження поза діапазоном.</b> <i>Від&rsquo;ємне</i> навантаження &mdash; це "
            "нормально: воно просто означає, що змінна пов&rsquo;язана з фактором обернено "
            "(реверсивний пункт); інтерпретуйте його величину як зазвичай. Навантаження чи "
            "спільність <i>понад 1</i> (рівнозначно від&rsquo;ємна унікальність) &mdash; це "
            "<b>випадок Хейвуда</b>: неналежний розв&rsquo;язок. У косокутній матриці <i>патерну</i> "
            "значення трохи понад 1 може виникнути правомірно, коли фактори сильно корельовані "
            "(ваги на кшталт регресійних, а не кореляції), проте спільність &gt; 1 завжди "
            "некоректна. Зазвичай це сигналізує про надмірно виділену модель (забагато факторів для "
            "даних), малу вибірку або майже колінеарні / дубльовані пункти. Типові виправлення: "
            "виділити менше факторів, прибрати надлишкові пункти, зібрати більше даних або "
            "спробувати інше виділення/обертання.</li>"
            "<li><b>Нумерація змінних.</b> &lsquo;Нумерувати змінні в таблицях&rsquo; замінює назви "
            "змінних у таблицях (KMO/MSA, навантаження, структура) номерами (1, 2, 3&hellip;) і додає "
            "нумеровану легенду до примітки кожної таблиці.</li>"
            "</ul>"
        ),
    },
    "confirmatory_factor_analysis.fine_print": {
        "en": (
            "<b>Methodology &amp; assumptions</b>"
            "<ul>"
            "<li><b>Estimation.</b> Maximum-likelihood fit of the user-specified measurement model to "
            "the sample covariance matrix (rows with any missing value are dropped list-wise; ordinal "
            "items are scored numerically). Each factor's variance is fixed to 1 for identification, so "
            "every factor needs at least two indicators.</li>"
            "<li><b>Loadings.</b> Reported as the <i>standardised</i> solution, so each loading is the "
            "indicator&ndash;factor correlation (roughly in &minus;1..1) and is comparable across "
            "indicators. A negative loading just means an inverse (reverse-keyed) relationship; "
            "interpret its magnitude. Loadings are sign-normalised so each factor's dominant direction "
            "is positive.</li>"
            "<li><b>Fit indices.</b> <b>&chi;&sup2;</b> tests <i>exact</i> fit (non-significant = good, "
            "but it is sensitive to sample size). <b>RMSEA</b>: &lt; .05 good, &lt; .08 acceptable, "
            "&lt; .10 mediocre, otherwise poor. <b>CFI / TLI</b>: &ge; .95 excellent, &ge; .90 "
            "acceptable, otherwise poor. <b>SRMR</b>: &le; .08 good, otherwise poor. <b>df</b> are the "
            "model degrees of freedom.</li>"
            "<li><b>Factor correlations.</b> With &lsquo;Allow factor correlation&rsquo; the factors may "
            "correlate (oblique model) and a factor-correlation matrix (&Phi;) is reported; otherwise "
            "the factors are constrained orthogonal.</li>"
            "<li><b>Loading significance.</b> With &lsquo;Verbal indicators in tables&rsquo; on, each "
            "estimated loading is starred from a Wald test (* p &lt; .05, ** .01, *** .001). The "
            "standard errors are <i>asymptotic</i> &mdash; from the numerical Hessian of the ML "
            "discrepancy, Cov(&theta;) &asymp; (2/N)&middot;H&#8315;&sup1; &mdash; so treat them as "
            "approximate, especially in small samples. Modification indices are not provided.</li>"
            "<li><b>Verbal indicators.</b> &lsquo;Verbal indicators in tables&rsquo; adds an "
            "Interpretation column to the fit-index table.</li>"
            "<li><b>Numbered variables.</b> &lsquo;Number variables in tables&rsquo; replaces the "
            "indicator names in the loadings table with numbers (1, 2, 3&hellip;) and adds a numbered "
            "legend to the table&rsquo;s note.</li>"
            "<li><b>Reproducibility.</b> Optimisation uses a fixed random seed, so re-running the same "
            "model gives the same solution. A non-convergence warning means the estimate may be "
            "unreliable.</li>"
            "</ul>"
        ),
        "ua": (
            "<b>Методологія та припущення</b>"
            "<ul>"
            "<li><b>Оцінювання.</b> Підгонка методом максимальної правдоподібності заданої "
            "користувачем вимірювальної моделі до вибіркової коваріаційної матриці (рядки з будь-яким "
            "пропущеним значенням вилучаються списково; порядкові пункти оцінюються числово). "
            "Дисперсія кожного фактора фіксується на 1 для ідентифікації, тож кожен фактор потребує "
            "щонайменше двох індикаторів.</li>"
            "<li><b>Навантаження.</b> Наводяться як <i>стандартизований</i> розв&rsquo;язок, тож "
            "кожне навантаження &mdash; це кореляція індикатор&ndash;фактор (приблизно в &minus;1..1) "
            "і зіставне між індикаторами. Від&rsquo;ємне навантаження просто означає обернений "
            "(реверсивний) зв&rsquo;язок; інтерпретуйте його величину. Навантаження "
            "знаково-нормалізовані, тож домінантний напрям кожного фактора додатний.</li>"
            "<li><b>Індекси відповідності.</b> <b>&chi;&sup2;</b> перевіряє <i>точну</i> "
            "відповідність (незначущий = добре, але чутливий до розміру вибірки). <b>RMSEA</b>: "
            "&lt; .05 добре, &lt; .08 прийнятно, &lt; .10 посередньо, інакше погано. <b>CFI / TLI</b>: "
            "&ge; .95 відмінно, &ge; .90 прийнятно, інакше погано. <b>SRMR</b>: &le; .08 добре, інакше "
            "погано. <b>df</b> &mdash; це ступені свободи моделі.</li>"
            "<li><b>Кореляції факторів.</b> З &lsquo;Дозволити кореляцію факторів&rsquo; фактори "
            "можуть корелювати (косокутна модель) і наводиться матриця кореляцій факторів (&Phi;); "
            "інакше фактори обмежені як ортогональні.</li>"
            "<li><b>Значущість навантажень.</b> З увімкненими &lsquo;Словесними індикаторами в "
            "таблицях&rsquo; кожне оцінене навантаження позначається зірочками за тестом Вальда "
            "(* p &lt; .05, ** .01, *** .001). Стандартні похибки <i>асимптотичні</i> &mdash; з "
            "числового гессіана розбіжності ML, Cov(&theta;) &asymp; (2/N)&middot;H&#8315;&sup1; "
            "&mdash; тож сприймайте їх як наближені, особливо на малих вибірках. Індекси модифікації "
            "не надаються.</li>"
            "<li><b>Словесні індикатори.</b> &lsquo;Словесні індикатори в таблицях&rsquo; додають "
            "стовпець Інтерпретація до таблиці індексів відповідності.</li>"
            "<li><b>Нумерація змінних.</b> &lsquo;Нумерувати змінні в таблицях&rsquo; замінює назви "
            "індикаторів у таблиці навантажень номерами (1, 2, 3&hellip;) і додає нумеровану легенду "
            "до примітки таблиці.</li>"
            "<li><b>Відтворюваність.</b> Оптимізація використовує фіксований випадковий seed, тож "
            "повторний запуск тієї самої моделі дає той самий розв&rsquo;язок. Попередження про "
            "незбіжність означає, що оцінка може бути ненадійною.</li>"
            "</ul>"
        ),
    },
    "cluster_analysis.fine_print": {
        "en": (
            "<b>Methodology &amp; assumptions</b>"
            "<ul>"
            "<li><b>Algorithm.</b> <b>K-means</b> (Lloyd's algorithm, 10 random initialisations, fixed "
            "seed so a re-run reproduces the result) or <b>Hierarchical</b> agglomerative clustering "
            "(Ward / average / complete / single linkage, cut to k clusters), which also draws a "
            "dendrogram. You set the number of clusters k in advance. Rows with any missing value are "
            "dropped (list-wise) and ordinal items are scored numerically.</li>"
            "<li><b>Standardisation.</b> K-means uses Euclidean distance, so variables on larger scales "
            "dominate. &lsquo;Standardise variables&rsquo; z-scores each variable first (recommended "
            "when variables are on different scales); centroids are always reported back in the "
            "original units.</li>"
            "<li><b>Quality.</b> The mean silhouette (&minus;1..1) measures how well each point sits in "
            "its cluster vs the nearest other cluster: &gt; .7 strong, &gt; .5 reasonable, &gt; .25 "
            "weak, otherwise no substantial structure. Inertia is the total within-cluster sum of "
            "squared distances (lower is tighter, but it always falls as k grows).</li>"
            "<li><b>Plot.</b> The scatter shows the clusters in two dimensions: the two variables "
            "directly when exactly two are selected, otherwise the first two principal components "
            "(with the % of variance each captures).</li>"
            "<li><b>Choosing k.</b> The method does not choose k for you. Use the silhouette-by-k plot "
            "(both methods) and, for K-means, the inertia &lsquo;elbow&rsquo; plot (both sweep k = "
            "2..10) together with domain knowledge.</li>"
            "<li><b>Caveat.</b> K-means assumes roughly spherical, similarly-sized clusters and is "
            "sensitive to outliers and the starting seed; standardise when variables differ in scale "
            "and treat the partition as exploratory.</li>"
            "</ul>"
        ),
        "ua": (
            "<b>Методологія та припущення</b>"
            "<ul>"
            "<li><b>Алгоритм.</b> <b>K-середніх</b> (алгоритм Ллойда, 10 випадкових ініціалізацій, "
            "фіксований seed, тож повторний запуск відтворює результат) або <b>Ієрархічна</b> "
            "агломеративна кластеризація (зв&rsquo;язок Ward / середній / повний / одиничний, "
            "розрізана на k кластерів), що також малює дендрограму. Кількість кластерів k ви задаєте "
            "заздалегідь. Рядки з будь-яким пропущеним значенням вилучаються (списково), а порядкові "
            "пункти оцінюються числово.</li>"
            "<li><b>Стандартизація.</b> K-середніх використовує евклідову відстань, тож змінні з "
            "більшими масштабами домінують. &lsquo;Стандартизувати змінні&rsquo; спершу z-стандартизує "
            "кожну змінну (рекомендовано, коли змінні на різних шкалах); центроїди завжди наводяться "
            "назад у вихідних одиницях.</li>"
            "<li><b>Якість.</b> Середній силует (&minus;1..1) вимірює, наскільки добре кожна точка "
            "розташована у своєму кластері порівняно з найближчим іншим: &gt; .7 сильна, &gt; .5 "
            "помірна, &gt; .25 слабка, інакше немає істотної структури. Інерція &mdash; це загальна "
            "внутрішньокластерна сума квадратів відстаней (менша = щільніше, але вона завжди спадає "
            "зі зростанням k).</li>"
            "<li><b>Графік.</b> Діаграма розсіювання показує кластери у двох вимірах: дві змінні "
            "безпосередньо, коли обрано рівно дві, інакше перші дві головні компоненти (з % дисперсії, "
            "яку кожна охоплює).</li>"
            "<li><b>Вибір k.</b> Метод не обирає k за вас. Використовуйте графік силуету за k "
            "(обидва методи) і, для K-середніх, графік &lsquo;ліктя&rsquo; інерції (обидва "
            "перебирають k = 2..10) разом із предметними знаннями.</li>"
            "<li><b>Застереження.</b> K-середніх припускає приблизно сферичні кластери схожого "
            "розміру й чутливий до викидів та стартового seed; стандартизуйте, коли змінні "
            "відрізняються за масштабом, і сприймайте розбиття як розвідувальне.</li>"
            "</ul>"
        ),
    },
    "paired.fine_print": {
        "en": (
            "<b>Methodology &amp; assumptions</b>"
            "<ul>"
            "<li><b>Design.</b> The selected variables are treated as repeated measurements of a "
            "single within-subject factor (e.g. time points or conditions on the same respondents). "
            "Only complete cases are used &mdash; a respondent missing any condition is dropped "
            "(listwise).</li>"
            "<li><b>Test selection.</b> Two conditions use the paired-samples family; three or more "
            "use the repeated-measures family. Parametric tests are used when the normality check "
            "passes; otherwise the non-parametric equivalents are used.</li>"
            "<li><b>Normality.</b> Shapiro&ndash;Wilk. For two conditions it is computed on the "
            "paired differences; for three or more it is computed per condition. The data are treated "
            "as normal only when every check passes (p &gt; .05).</li>"
            "<li><b>Parametric, 2 conditions.</b> Paired-samples t-test; effect size Cohen&rsquo;s "
            "d<sub>z</sub> = mean(difference) / SD(difference).</li>"
            "<li><b>Parametric, 3+ conditions.</b> One-way repeated-measures ANOVA; effect size "
            "generalised &eta;&sup2;<sub>G</sub>. Sphericity is tested with Mauchly&rsquo;s test and "
            "the Greenhouse&ndash;Geisser&ndash;corrected p-value (with &epsilon;) is reported "
            "alongside the uncorrected one.</li>"
            "<li><b>Non-parametric, 2 conditions.</b> Wilcoxon signed-rank test; effect size the "
            "matched-pairs rank-biserial correlation.</li>"
            "<li><b>Non-parametric, 3+ conditions.</b> Friedman test; effect size Kendall&rsquo;s "
            "W.</li>"
            "<li><b>Post-hoc</b> (only when &lsquo;Effect size / Post-hoc&rsquo; is on, three or more "
            "conditions, and the omnibus test is significant): parametric &rarr; pairwise paired "
            "t-tests with Holm correction; non-parametric &rarr; Nemenyi test.</li>"
            "<li><b>Verbal indicators.</b> &lsquo;Verbal indicators in tables&rsquo; adds plain-language "
            "columns next to each p-value (Significant? / Normal? at &alpha; = .05) and a Magnitude "
            "column for the effect size (Cohen&rsquo;s d by |d| 0.2 / 0.5 / 0.8; the rank-biserial r "
            "by the correlation bands |r| .1 / .3 / .5).</li>"
            "<li><b>Numbered conditions.</b> &lsquo;Number conditions in tables&rsquo; replaces the "
            "condition names in the tables with numbers (1, 2, 3&hellip;) and adds a numbered legend to "
            "each table&rsquo;s note; the verbal summary keeps the real names.</li>"
            "<li><b>Threshold.</b> All tests are two-sided and use &alpha; = .05.</li>"
            "</ul>"
        ),
        "ua": (
            "<b>Методологія та припущення</b>"
            "<ul>"
            "<li><b>Дизайн.</b> Обрані змінні розглядаються як повторні вимірювання одного "
            "внутрішньосуб&rsquo;єктного фактора (наприклад, моменти часу чи умови на тих самих "
            "респондентах). Використовуються лише повні випадки &mdash; респондента, у якого "
            "пропущено будь-яку умову, вилучають (списково).</li>"
            "<li><b>Вибір тесту.</b> Дві умови використовують родину парних вибірок; три і більше "
            "&mdash; родину повторних вимірювань. Параметричні тести застосовуються, коли перевірка "
            "на нормальність проходить; інакше використовуються непараметричні відповідники.</li>"
            "<li><b>Нормальність.</b> Шапіро&ndash;Вілк. Для двох умов обчислюється на парних "
            "різницях; для трьох і більше &mdash; для кожної умови. Дані вважаються нормальними лише "
            "тоді, коли кожна перевірка проходить (p &gt; .05).</li>"
            "<li><b>Параметричний, 2 умови.</b> t-тест для парних вибірок; розмір ефекту d Коена "
            "d<sub>z</sub> = середнє(різниці) / SD(різниці).</li>"
            "<li><b>Параметричний, 3+ умов.</b> Однофакторний ANOVA з повторними вимірюваннями; "
            "розмір ефекту узагальнена &eta;&sup2;<sub>G</sub>. Сферичність перевіряється тестом "
            "Маучлі, і p-значення з поправкою Грінхауса&ndash;Гайссера (з &epsilon;) наводиться "
            "поряд із непоправленим.</li>"
            "<li><b>Непараметричний, 2 умови.</b> Знаково-ранговий тест Вілкоксона; розмір ефекту "
            "&mdash; рангово-бісеріальна кореляція для парних спостережень.</li>"
            "<li><b>Непараметричний, 3+ умов.</b> Тест Фрідмана; розмір ефекту W Кендала.</li>"
            "<li><b>Апостеріорні</b> (лише коли увімкнено &lsquo;Розмір ефекту / Апостеріорні&rsquo;, "
            "три і більше умов та омнібусний тест значущий): параметричні &rarr; попарні парні "
            "t-тести з поправкою Холма; непараметричні &rarr; тест Немені.</li>"
            "<li><b>Словесні індикатори.</b> &lsquo;Словесні індикатори в таблицях&rsquo; додають "
            "стовпці звичайною мовою поруч із кожним p-значенням (Значущо? / Нормально? при "
            "&alpha; = .05) і стовпець Величина для розміру ефекту (d Коена за |d| 0.2 / 0.5 / 0.8; "
            "рангово-бісеріальний r за смугами кореляції |r| .1 / .3 / .5).</li>"
            "<li><b>Нумерація умов.</b> &lsquo;Нумерувати умови в таблицях&rsquo; замінює назви умов у "
            "таблицях номерами (1, 2, 3&hellip;) і додає нумеровану легенду до примітки кожної "
            "таблиці; словесний підсумок зберігає справжні назви.</li>"
            "<li><b>Поріг.</b> Усі тести двосторонні та використовують &alpha; = .05.</li>"
            "</ul>"
        ),
    },
    "contingency.fine_print": {
        "en": (
            "<b>Methodology &amp; assumptions</b>"
            "<ul>"
            "<li><b>Test.</b> Pearson&rsquo;s chi-square test of independence on the cross-tabulation "
            "of the two variables.</li>"
            "<li><b>Continuity correction.</b> Yates&rsquo; correction only affects 2&times;2 tables. "
            "The &ldquo;Continuity correction&rdquo; switch (on by default) is applied consistently to "
            "<i>both</i> the reported &chi;<sup>2</sup> and the effect size. Note that effect sizes are "
            "conventionally computed from the <i>uncorrected</i> &chi;<sup>2</sup> &mdash; turn the "
            "switch off to follow that convention. For tables larger than 2&times;2 it has no effect.</li>"
            "<li><b>Effect size.</b> &phi; (phi) for 2&times;2 tables, Cramer&rsquo;s V otherwise, with "
            "V = &radic;(&chi;<sup>2</sup> / (N&middot;(min(r,c)&minus;1))). Interpretation thresholds: "
            "&lt; 0.2 weak, &lt; 0.6 moderate, otherwise strong.</li>"
            "<li><b>Verbal indicators.</b> &lsquo;Verbal indicators in tables&rsquo; adds a Significant? "
            "conclusion next to the &chi;<sup>2</sup> p-value and, when an effect size is shown, a "
            "Magnitude column (weak / moderate / strong by the thresholds above).</li>"
            "<li><b>Small samples.</b> The chi-square test assumes expected cell counts &ge; 5. For "
            "2&times;2 tables where this is violated, Fisher&rsquo;s exact test (two-sided) is reported "
            "instead; for larger tables a low-count chi-square should be interpreted with caution.</li>"
            "<li><b>Paired data (symmetry test).</b> When &lsquo;Paired data&rsquo; is enabled and the "
            "two variables form a square table with matching categories on both axes (the same items "
            "measured twice), a symmetry test is added: <b>McNemar&rsquo;s test</b> for 2&times;2 "
            "tables (exact binomial when the discordant count is &lt; 25, otherwise &chi;<sup>2</sup> "
            "with the continuity correction following the same switch) and <b>Bowker&rsquo;s test of "
            "symmetry</b> for larger square tables. If the table is not square it is skipped with a "
            "note.</li>"
            "<li><b>Threshold.</b> Tests are two-sided and use &alpha; = .05.</li>"
            "<li><b>Missing data.</b> Rows with a missing value in either variable are excluded "
            "(pairwise).</li>"
            "</ul>"
        ),
        "ua": (
            "<b>Методологія та припущення</b>"
            "<ul>"
            "<li><b>Тест.</b> Тест незалежності хі-квадрат Пірсона на таблиці сполученості двох "
            "змінних.</li>"
            "<li><b>Поправка на неперервність.</b> Поправка Йейтса впливає лише на таблиці 2&times;2. "
            "Перемикач &ldquo;Поправка на неперервність&rdquo; (увімкнений за замовчуванням) "
            "застосовується узгоджено <i>як</i> до наведеного &chi;<sup>2</sup>, так і до розміру "
            "ефекту. Зауважте, що розміри ефекту за традицією обчислюються з <i>непоправленого</i> "
            "&chi;<sup>2</sup> &mdash; вимкніть перемикач, щоб дотримуватися цієї традиції. Для "
            "таблиць більших за 2&times;2 вона не діє.</li>"
            "<li><b>Розмір ефекту.</b> &phi; (фі) для таблиць 2&times;2, інакше V Крамера, де "
            "V = &radic;(&chi;<sup>2</sup> / (N&middot;(min(r,c)&minus;1))). Пороги інтерпретації: "
            "&lt; 0.2 слабкий, &lt; 0.6 помірний, інакше сильний.</li>"
            "<li><b>Словесні індикатори.</b> &lsquo;Словесні індикатори в таблицях&rsquo; додають "
            "висновок Значущо? поруч із p-значенням &chi;<sup>2</sup> і, коли показано розмір ефекту, "
            "стовпець Величина (слабкий / помірний / сильний за порогами вище).</li>"
            "<li><b>Малі вибірки.</b> Тест хі-квадрат припускає очікувані частоти комірок &ge; 5. "
            "Для таблиць 2&times;2, де це порушено, натомість наводиться точний тест Фішера "
            "(двосторонній); для більших таблиць хі-квадрат із малими частотами слід інтерпретувати "
            "обережно.</li>"
            "<li><b>Парні дані (тест симетрії).</b> Коли увімкнено &lsquo;Парні дані&rsquo; і дві "
            "змінні утворюють квадратну таблицю з однаковими категоріями по обох осях (ті самі "
            "об&rsquo;єкти, виміряні двічі), додається тест симетрії: <b>тест Мак-Немара</b> для "
            "таблиць 2&times;2 (точний біноміальний, коли кількість розбіжних &lt; 25, інакше "
            "&chi;<sup>2</sup> з поправкою на неперервність за тим самим перемикачем) та <b>тест "
            "симетрії Боукера</b> для більших квадратних таблиць. Якщо таблиця не квадратна, його "
            "пропущено з приміткою.</li>"
            "<li><b>Поріг.</b> Тести двосторонні та використовують &alpha; = .05.</li>"
            "<li><b>Пропущені дані.</b> Рядки з пропущеним значенням у будь-якій зі змінних "
            "виключаються (попарно).</li>"
            "</ul>"
        ),
    },
    "descriptive.fine_print": {
        "en": (
            "<b>Methodology &amp; assumptions</b>"
            "<ul>"
            "<li><b>Numeric summary.</b> N, missing, mean, SD, min and max; optionally (Extended "
            "stats) median, Q1/Q3 (IQR), the standard error of the mean, and skewness &amp; "
            "kurtosis (Fisher / excess, so a normal distribution has 0).</li>"
            "<li><b>Normality.</b> A selectable test &mdash; Shapiro&ndash;Wilk (W), "
            "Kolmogorov&ndash;Smirnov (D, against a normal with the sample mean &amp; SD; the basic "
            "KS, not Lilliefors-corrected) or Anderson&ndash;Darling (A&sup2;, p-value via Stephens' "
            "approximation) &mdash; needs N &ge; 3. Shown as a separate table plus a verbal summary. "
            "<i>Which to use:</i> Shapiro&ndash;Wilk is the most powerful general choice and is "
            "recommended for small-to-moderate samples (roughly N &le; 50, valid up to a few thousand); "
            "Anderson&ndash;Darling is more sensitive to departures in the tails and works well on "
            "larger samples; the basic Kolmogorov&ndash;Smirnov is the least powerful (it is "
            "conservative when the mean/SD are estimated) and is offered mainly for comparability with "
            "older reports. With large N any test flags trivial deviations, so pair it with the Q-Q "
            "plot and skewness/kurtosis.</li>"
            "<li><b>Categorical summary.</b> A per-variable frequency table with counts and "
            "percentages (of non-missing) is shown for non-numeric variables.</li>"
            "<li><b>Histograms.</b> Densities. Bin width is automatic (Freedman&ndash;Diaconis / "
            "&lsquo;auto&rsquo;) unless a Bin width is given &mdash; set it to 1 for Likert-type "
            "scales so each value is its own bar. A Bin reference value, if given, becomes the centre "
            "of one bin (the rest follow the width).</li>"
            "<li><b>KDE.</b> Gaussian kernel, Scott&rsquo;s-rule bandwidth multiplied by the KDE "
            "smoothing factor (1 = default; raise it to avoid a spiky curve on discrete/Likert "
            "data).</li>"
            "<li><b>Outliers.</b> Tukey outliers (beyond 1.5&times;IQR) are reported beneath the "
            "numeric summary table, naming each outlier&rsquo;s variable and group, with the full "
            "list of IDs (when an ID column is set) for easy copying. Box plots draw them as points; "
            "enable &lsquo;Label outliers&rsquo; to also tag each point on the plot.</li>"
            "<li><b>Q-Q plots.</b> Sample quantiles vs theoretical normal quantiles, with a "
            "reference line.</li>"
            "<li><b>Verbal indicators.</b> &lsquo;Verbal indicators in tables&rsquo; adds plain-language "
            "columns (e.g. the Normal? conclusion) to the tables; untick it for numbers only.</li>"
            "<li><b>Grouping.</b> A grouping column splits the numeric summary, distribution plots, "
            "box plots and the categorical frequency table/bars by group. Pie and Q-Q plots always "
            "use the whole variable.</li>"
            "<li><b>Numbered variables.</b> &lsquo;Number variables in tables&rsquo; replaces the "
            "variable names in the numeric-summary and normality tables with numbers (1, 2, 3&hellip;) "
            "and adds a numbered legend to each table&rsquo;s note.</li>"
            "<li><b>Missing data.</b> Each variable is summarised/plotted on its own non-missing "
            "values.</li>"
            "</ul>"
        ),
        "ua": (
            "<b>Методологія та припущення</b>"
            "<ul>"
            "<li><b>Числовий підсумок.</b> N, пропуски, середнє, SD, мінімум і максимум; за бажанням "
            "(Розширена статистика) медіана, Q1/Q3 (IQR), стандартна похибка середнього, а також "
            "асиметрія та ексцес (Фішерів / надлишковий, тож нормальний розподіл має 0).</li>"
            "<li><b>Нормальність.</b> Тест на вибір &mdash; Шапіро&ndash;Вілк (W), "
            "Колмогоров&ndash;Смирнов (D, проти нормального з вибірковим середнім та SD; базовий "
            "KS, без поправки Ліллієфорса) або Андерсон&ndash;Дарлінг (A&sup2;, p-значення за "
            "наближенням Стівенса) &mdash; потребує N &ge; 3. Показується окремою таблицею плюс "
            "словесний підсумок. <i>Що обрати:</i> Шапіро&ndash;Вілк &mdash; найпотужніший загальний "
            "вибір, рекомендований для малих і середніх вибірок (приблизно N &le; 50, дійсний до "
            "кількох тисяч); Андерсон&ndash;Дарлінг чутливіший до відхилень у хвостах і добре працює "
            "на більших вибірках; базовий Колмогоров&ndash;Смирнов найменш потужний (консервативний, "
            "коли середнє/SD оцінено) і пропонується переважно для сумісності зі старішими звітами. "
            "За великого N будь-який тест відмічає незначні відхилення, тож поєднуйте його з "
            "Q-Q графіком та асиметрією/ексцесом.</li>"
            "<li><b>Категоріальний підсумок.</b> Для нечислових змінних показується таблиця частот "
            "для кожної змінної з підрахунками та відсотками (від непропущених).</li>"
            "<li><b>Гістограми.</b> Густини. Ширина інтервалу автоматична "
            "(Фрідмен&ndash;Діаконіс / &lsquo;auto&rsquo;), якщо не задано Ширину інтервалу &mdash; "
            "встановіть її 1 для шкал типу Лайкерта, щоб кожне значення мало власний стовпчик. "
            "Опорне значення інтервалу, якщо задано, стає центром одного інтервалу (решта йдуть за "
            "шириною).</li>"
            "<li><b>KDE.</b> Гаусове ядро, ширина смуги за правилом Скотта, помножена на коефіцієнт "
            "згладжування KDE (1 = за замовчуванням; підвищіть його, щоб уникнути гострої кривої на "
            "дискретних/Лайкертових даних).</li>"
            "<li><b>Викиди.</b> Викиди Тьюкі (за межами 1.5&times;IQR) наводяться під таблицею "
            "числового підсумку, із зазначенням змінної та групи кожного викиду, з повним списком "
            "ID (коли задано стовпець ID) для зручного копіювання. Діаграми розмаху малюють їх "
            "точками; увімкніть &lsquo;Підписувати викиди&rsquo;, щоб також позначити кожну точку на "
            "графіку.</li>"
            "<li><b>Графіки Q-Q.</b> Вибіркові квантилі проти теоретичних нормальних квантилів, з "
            "лінією відліку.</li>"
            "<li><b>Словесні індикатори.</b> &lsquo;Словесні індикатори в таблицях&rsquo; додають до "
            "таблиць стовпці звичайною мовою (наприклад, висновок Нормально?); зніміть позначку для "
            "лише чисел.</li>"
            "<li><b>Групування.</b> Стовпець групування розбиває числовий підсумок, графіки "
            "розподілу, діаграми розмаху та таблицю/стовпці частот категорій за групами. Кругові "
            "діаграми та графіки Q-Q завжди використовують усю змінну.</li>"
            "<li><b>Нумерація змінних.</b> &lsquo;Нумерувати змінні в таблицях&rsquo; замінює назви "
            "змінних у таблицях числового підсумку та нормальності номерами (1, 2, 3&hellip;) і додає "
            "нумеровану легенду до примітки кожної таблиці.</li>"
            "<li><b>Пропущені дані.</b> Кожна змінна підсумовується/будується на власних "
            "непропущених значеннях.</li>"
            "</ul>"
        ),
    },
}


def t(key: str, **kwargs) -> str:
    """Return the template for ``key`` in the active language (English fallback),
    formatted with ``kwargs``."""
    entry = TRANSLATIONS[key]
    template = entry.get(LANGUAGE.language.value, entry["en"])
    return template.format(**kwargs)
