args <- commandArgs(trailingOnly = TRUE)
output_path <- if (length(args) >= 1) {
  args[[1]]
} else {
  file.path("tests", "benchmarks", "mean_comparison", "benchmarks", "mean_comparison_r_benchmarks.json")
}

for (pkg in c("jsonlite", "car", "PMCMRplus")) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    stop(sprintf("Package '%s' is required. Install with install.packages('%s').", pkg, pkg), call. = FALSE)
  }
}

two_g <- factor(c(rep("A", 6), rep("B", 6)), levels = c("A", "B"))
two_y <- c(10, 12, 11, 13, 9, 14, 15, 18, 16, 20, 14, 19)
three_g <- factor(c(rep("A", 5), rep("B", 5), rep("C", 5)), levels = c("A", "B", "C"))
three_y <- c(10, 12, 11, 13, 9, 15, 18, 16, 20, 14, 8, 7, 9, 6, 10)

num <- function(v) as.numeric(v)

# 95% CI for Cohen's d from its large-sample SE (the form StatPrism uses).
cohen_d_ci <- function(d, n1, n2) {
  se <- sqrt((n1 + n2) / (n1 * n2) + d^2 / (2 * (n1 + n2)))
  list(low = d - 1.96 * se, high = d + 1.96 * se)
}

# Pairs from a PMCMRplus lower-triangular p-value matrix, keyed "<row>__<col>".
pmcmr_pairs <- function(pv) {
  out <- list()
  for (r in rownames(pv)) {
    for (c in colnames(pv)) {
      if (!is.na(pv[r, c])) {
        out[[paste0(r, "__", c)]] <- num(pv[r, c])
      }
    }
  }
  out
}

ttest_homogeneous <- function() {
  a <- two_y[two_g == "A"]
  b <- two_y[two_g == "B"]
  tt <- t.test(a, b, var.equal = TRUE)
  n1 <- length(a)
  n2 <- length(b)
  pooled <- sqrt(((n1 - 1) * sd(a)^2 + (n2 - 1) * sd(b)^2) / (n1 + n2 - 2))
  d <- (mean(a) - mean(b)) / pooled
  ci <- cohen_d_ci(d, n1, n2)
  list(
    error = "", t = num(tt$statistic), p = num(tt$p.value), df = num(tt$parameter),
    mean1 = num(mean(a)), sd1 = num(sd(a)), mean2 = num(mean(b)), sd2 = num(sd(b)),
    cohen_d = num(d), ci_low = num(ci$low), ci_high = num(ci$high)
  )
}

ttest_welch <- function() {
  a <- two_y[two_g == "A"]
  b <- two_y[two_g == "B"]
  tt <- t.test(a, b, var.equal = FALSE)
  # Welch Cohen's d: root-mean of the two group variances (not the pooled SD).
  denom <- sqrt((sd(a)^2 + sd(b)^2) / 2)
  d <- (mean(a) - mean(b)) / denom
  ci <- cohen_d_ci(d, length(a), length(b))
  list(
    error = "", t = num(tt$statistic), p = num(tt$p.value), df = num(tt$parameter),
    mean1 = num(mean(a)), sd1 = num(sd(a)), mean2 = num(mean(b)), sd2 = num(sd(b)),
    cohen_d = num(d), ci_low = num(ci$low), ci_high = num(ci$high)
  )
}

mann_whitney <- function() {
  a <- two_y[two_g == "A"]
  b <- two_y[two_g == "B"]
  w <- suppressWarnings(wilcox.test(a, b))
  u1 <- num(w$statistic) # R's W equals scipy's U for the first sample
  n1 <- length(a)
  n2 <- length(b)
  list(
    error = "", u = min(u1, n1 * n2 - u1), p = num(w$p.value),
    rank_biserial = 1 - 2 * u1 / (n1 * n2),
    median1 = num(median(a)), iqr1 = num(IQR(a, type = 7)),
    median2 = num(median(b)), iqr2 = num(IQR(b, type = 7))
  )
}

anova_oneway <- function() {
  fit <- aov(three_y ~ three_g)
  s <- summary(fit)[[1]]
  ss <- s[["Sum Sq"]]
  list(
    error = "", f = num(s[["F value"]][1]), p = num(s[["Pr(>F)"]][1]),
    df_between = num(s[["Df"]][1]), df_within = num(s[["Df"]][2]),
    eta2 = num(ss[1] / sum(ss))
  )
}

anova_welch <- function() {
  ow <- oneway.test(three_y ~ three_g, var.equal = FALSE)
  list(
    error = "", f = num(ow$statistic), p = num(ow$p.value),
    df_between = num(ow$parameter[1]), df_within = num(ow$parameter[2])
  )
}

kruskal <- function() {
  k <- kruskal.test(three_y ~ three_g)
  list(error = "", h = num(k$statistic), p = num(k$p.value), df = num(k$parameter))
}

normality_shapiro <- function() {
  a <- shapiro.test(two_y[two_g == "A"])
  b <- shapiro.test(two_y[two_g == "B"])
  list(error = "", groups = list(
    A = list(w = num(a$statistic), p = num(a$p.value)),
    B = list(w = num(b$statistic), p = num(b$p.value))
  ))
}

homogeneity_levene <- function() {
  lv <- car::leveneTest(two_y ~ two_g, center = mean)
  list(error = "", f = num(lv[["F value"]][1]), p = num(lv[["Pr(>F)"]][1]))
}

posthoc_tukey <- function() {
  th <- TukeyHSD(aov(three_y ~ three_g))$three_g
  pairs <- list()
  for (rn in rownames(th)) {
    pairs[[gsub("-", "__", rn)]] <- num(th[rn, "p adj"])
  }
  list(error = "", pairs = pairs)
}

posthoc_tamhane <- function() {
  pv <- suppressWarnings(PMCMRplus::tamhaneT2Test(three_y, three_g)$p.value)
  list(error = "", pairs = pmcmr_pairs(pv))
}

posthoc_dunn <- function() {
  pv <- suppressWarnings(PMCMRplus::kwAllPairsDunnTest(three_y, three_g, p.adjust.method = "none")$p.value)
  list(error = "", pairs = pmcmr_pairs(pv))
}

benchmarks <- list(
  tolerance = 1e-6,
  generated_by = "tests/benchmarks/mean_comparison/r/generate_mean_comparison_benchmarks.R",
  studies = list(
    ttest_homogeneous = ttest_homogeneous(),
    ttest_welch = ttest_welch(),
    mann_whitney = mann_whitney(),
    anova_oneway = anova_oneway(),
    anova_welch = anova_welch(),
    kruskal = kruskal(),
    normality_shapiro = normality_shapiro(),
    homogeneity_levene = homogeneity_levene(),
    posthoc_tukey = posthoc_tukey(),
    posthoc_tamhane = posthoc_tamhane(),
    posthoc_dunn = posthoc_dunn()
  )
)

dir.create(dirname(output_path), recursive = TRUE, showWarnings = FALSE)
jsonlite::write_json(benchmarks, output_path, auto_unbox = TRUE, pretty = TRUE, null = "null", na = "null", digits = NA)
cat("Wrote", output_path, "\n")
