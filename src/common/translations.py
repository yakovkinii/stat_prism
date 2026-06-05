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
        "en": "The Cramer's V = {v}, indicating a {interpretation} between {col1} and {col2}.",
        "ua": "V Крамера = {v}, що свідчить про {interpretation} між {col1} та {col2}.",
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
    # ----- Reliability -----
    "reliability.caption.cronbach": {
        "en": "Cronbach's Alpha",
        "ua": "Альфа Кронбаха",
    },
    "reliability.msg.binary_required": {
        "en": "All columns must have at most 2 unique values for the selected correlation type",
        "ua": "Усі стовпці повинні мати щонайбільше 2 унікальні значення для обраного типу кореляції",
    },
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
    "correlation.sign.positive": {"en": "positive", "ua": "позитивну"},
    "correlation.sign.negative": {"en": "negative", "ua": "негативну"},
    "correlation.report.intro": {
        "en": "A {name} was calculated to assess the relationship between the variables {vars} (Table {table}). ",
        "ua": "Розраховано {name} для оцінки зв'язку між змінними {vars} (Таблиця {table}). ",
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
    "correlation.table.caption": {
        "en": "{name} between {vars}.",
        "ua": "{name} між {vars}.",
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
}


def t(key: str, **kwargs) -> str:
    """Return the template for ``key`` in the active language (English fallback),
    formatted with ``kwargs``."""
    entry = TRANSLATIONS[key]
    template = entry.get(LANGUAGE.language.value, entry["en"])
    return template.format(**kwargs)
