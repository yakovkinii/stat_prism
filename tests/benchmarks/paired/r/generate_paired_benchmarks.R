args <- commandArgs(trailingOnly = TRUE)
output_path <- if (length(args) >= 1) {
  args[[1]]
} else {
  file.path("tests", "benchmarks", "paired", "benchmarks", "paired_r_benchmarks.json")
}

for (pkg in c("jsonlite", "car", "PMCMRplus")) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    stop(sprintf("Package '%s' is required. Install with install.packages('%s').", pkg, pkg), call. = FALSE)
  }
}

# Two within-subject conditions (pre/post): differences are non-zero with distinct absolute values so
# R's exact Wilcoxon p matches scipy's exact p. Three within-subject conditions (repeated measures).
pre <- c(20, 22, 21, 23, 19, 24, 18, 25, 20, 22)
post <- c(23, 20, 26, 19, 25, 25, 10, 32, 11, 32)
t1 <- c(10, 12, 11, 13, 9, 14, 8, 15, 10, 12)
t2 <- c(13, 16, 14, 18, 11, 16, 12, 20, 12, 17)
t3 <- c(11, 10, 12, 9, 13, 10, 14, 11, 12, 10)
n <- 10

num <- function(v) as.numeric(v)

# One descriptives row (base R; IQR type 7 matches pandas' default linear quantiles).
desc_row <- function(x) {
  list(n = length(x), mean = num(mean(x)), sd = num(sd(x)), median = num(median(x)), iqr = num(IQR(x, type = 7)))
}

# Mauchly's test and the Greenhouse-Geisser correction at full precision, via car on the MLM
# (rstatix rounds its tables to 3 decimals, so it cannot be used for a 1e-6 comparison).
sphericity_fit <- function() {
  mlm <- lm(cbind(t1, t2, t3) ~ 1)
  av <- car::Anova(mlm, idata = data.frame(cond = factor(c("t1", "t2", "t3"))), idesign = ~cond, type = 3)
  summary(av, multivariate = FALSE)
}

paired_t <- function() {
  tt <- t.test(pre, post, paired = TRUE)
  d <- pre - post
  list(error = "", t = num(tt$statistic), p = num(tt$p.value), df = num(tt$parameter),
       cohen_dz = num(mean(d) / sd(d)))
}

wilcoxon <- function() {
  # scipy/pingouin report W = min(R+, R-) and the EXACT signed-rank p; the chosen data has no ties or
  # zeros so R's wilcox.test is also exact and agrees. R's V statistic is R+, so take the min to match.
  w <- wilcox.test(pre, post, paired = TRUE)
  d <- pre - post
  r <- rank(abs(d))
  r_pos <- sum(r[d > 0])
  r_neg <- sum(r[d < 0])
  list(error = "", w = num(min(r_pos, r_neg)), p = num(w$p.value),
       rbc = num((r_pos - r_neg) / (r_pos + r_neg)))
}

rm_anova <- function() {
  long <- data.frame(id = factor(rep(1:n, 3)), cond = factor(rep(c("t1", "t2", "t3"), each = n)),
                     val = c(t1, t2, t3))
  fit <- aov(val ~ cond + Error(id / cond), data = long)
  s <- summary(fit)
  within <- s[["Error: id:cond"]][[1]]
  ss_cond <- within[["Sum Sq"]][1]
  ss_resid <- within[["Sum Sq"]][2]
  ss_id <- s[["Error: id"]][[1]][["Sum Sq"]][1]
  # Generalized eta^2 for a one-within / no-between design: effect SS over all SS (effect + subject
  # stratum + within error). This matches pingouin's ng2 (partial eta^2 would use only effect + error).
  ng2 <- ss_cond / (ss_cond + ss_id + ss_resid)
  sm <- sphericity_fit()
  list(
    error = "", f = num(within[["F value"]][1]), df1 = num(within[["Df"]][1]),
    df2 = num(within[["Df"]][2]), p = num(within[["Pr(>F)"]][1]), ng2 = num(ng2),
    p_gg = num(sm$pval.adjustments[1, "Pr(>F[GG])"]), eps = num(sm$pval.adjustments[1, "GG eps"])
  )
}

friedman <- function() {
  fr <- friedman.test(cbind(t1, t2, t3))
  k <- 3
  # Kendall's W is the Friedman chi-square normalized: W = chi2 / (n * (k - 1)).
  list(error = "", chi2 = num(fr$statistic), df = num(fr$parameter), p = num(fr$p.value),
       kendall_w = num(fr$statistic / (n * (k - 1))))
}

descriptives_two <- function() list(error = "", rows = list(pre = desc_row(pre), post = desc_row(post)))

descriptives_three <- function() {
  list(error = "", rows = list(t1 = desc_row(t1), t2 = desc_row(t2), t3 = desc_row(t3)))
}

normality_two <- function() {
  sw <- shapiro.test(pre - post)
  list(error = "", differences = list(w = num(sw$statistic), p = num(sw$p.value)))
}

normality_three <- function() {
  sw <- function(x) {
    s <- shapiro.test(x)
    list(w = num(s$statistic), p = num(s$p.value))
  }
  sm <- sphericity_fit()
  list(
    error = "",
    conditions = list(t1 = sw(t1), t2 = sw(t2), t3 = sw(t3)),
    sphericity = list(w = num(sm$sphericity.tests[1, "Test statistic"]),
                      p = num(sm$sphericity.tests[1, "p-value"]))
  )
}

posthoc_param <- function() {
  # Per-pair paired t-tests with Holm adjustment (matches pingouin pairwise_tests, no pooled SD).
  raw <- c(
    t2__t1 = t.test(t2, t1, paired = TRUE)$p.value,
    t3__t1 = t.test(t3, t1, paired = TRUE)$p.value,
    t3__t2 = t.test(t3, t2, paired = TRUE)$p.value
  )
  adj <- p.adjust(raw, method = "holm")
  list(error = "", pairs = as.list(adj))
}

posthoc_nonparam <- function() {
  pv <- suppressWarnings(PMCMRplus::frdAllPairsNemenyiTest(
    y = c(t1, t2, t3), groups = factor(rep(c("t1", "t2", "t3"), each = n)),
    blocks = factor(rep(1:n, 3))
  )$p.value)
  list(error = "", pairs = list(
    t2__t1 = num(pv["t2", "t1"]), t3__t1 = num(pv["t3", "t1"]), t3__t2 = num(pv["t3", "t2"])
  ))
}

benchmarks <- list(
  tolerance = 1e-6,
  generated_by = "tests/benchmarks/paired/r/generate_paired_benchmarks.R",
  studies = list(
    paired_t = paired_t(),
    wilcoxon = wilcoxon(),
    rm_anova = rm_anova(),
    friedman = friedman(),
    descriptives_two = descriptives_two(),
    descriptives_three = descriptives_three(),
    normality_two = normality_two(),
    normality_three = normality_three(),
    posthoc_param = posthoc_param(),
    posthoc_nonparam = posthoc_nonparam()
  )
)

dir.create(dirname(output_path), recursive = TRUE, showWarnings = FALSE)
jsonlite::write_json(benchmarks, output_path, auto_unbox = TRUE, pretty = TRUE, null = "null", na = "null", digits = NA)
cat("Wrote", output_path, "\n")
