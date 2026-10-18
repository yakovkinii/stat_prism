args <- commandArgs(trailingOnly = TRUE)
output_path <- if (length(args) >= 1) {
  args[[1]]
} else {
  file.path("tests", "benchmarks", "descriptives", "benchmarks", "descriptives_r_benchmarks.json")
}

for (pkg in c("jsonlite", "e1071", "nortest")) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    stop(sprintf("Package '%s' is required. Install with install.packages('%s').", pkg, pkg), call. = FALSE)
  }
}

numeric_x <- c(12, 15, 14, 10, 18, 20, 13, 16, 11, 19, 17, 14, 15, 13, 21, 9, 16, 18, 12, 17, NA, NA)
skewed_x <- c(1, 1, 1, 2, 2, 2, 2, 3, 3, 4, 5, 7, 9, 12, 18, 25, 2, 1, 3, 6)
# Group "A" subset of grouped_data() in cases.py.
grouped_a_x <- c(12, 15, 14, 10, 18, 20, 13, 16, 11, 19)

clean_number <- function(v) {
  if (is.null(v) || length(v) == 0 || is.nan(v) || is.na(v)) NA_real_ else as.numeric(v)
}

numeric_summary <- function(x) {
  xo <- x[!is.na(x)]
  n <- length(xo)
  # Base R / e1071 reproduce StatPrism's pandas stats: sd = ddof 1, quantile type 7, skewness and
  # kurtosis = the bias-corrected (type 2 / G1, G2 excess) forms pandas uses.
  stats <- list(
    N = n,
    missing = sum(is.na(x)),
    mean = clean_number(mean(xo)),
    std = clean_number(sd(xo)),
    se = clean_number(sd(xo) / sqrt(n)),
    median = clean_number(median(xo)),
    q1 = clean_number(quantile(xo, 0.25, type = 7, names = FALSE)),
    q3 = clean_number(quantile(xo, 0.75, type = 7, names = FALSE)),
    skew = clean_number(e1071::skewness(xo, type = 2)),
    kurtosis = clean_number(e1071::kurtosis(xo, type = 2)),
    min = clean_number(min(xo)),
    max = clean_number(max(xo))
  )
  list(error = "", stats = stats)
}

normality <- function(x, test) {
  res <- switch(test,
    shapiro = shapiro.test(x),
    lilliefors = nortest::lillie.test(x),
    anderson_darling = nortest::ad.test(x)
  )
  list(error = "", statistic = clean_number(res$statistic), p = clean_number(res$p.value))
}

benchmarks <- list(
  tolerance = 1e-6,
  generated_by = "tests/benchmarks/descriptives/r/generate_descriptives_benchmarks.R",
  studies = list(
    numeric_summary = numeric_summary(numeric_x),
    normality_shapiro = normality(skewed_x, "shapiro"),
    normality_lilliefors = normality(skewed_x, "lilliefors"),
    normality_anderson_darling = normality(skewed_x, "anderson_darling"),
    summary_grouped = numeric_summary(grouped_a_x),
    normality_grouped = normality(grouped_a_x, "shapiro")
  )
)

dir.create(dirname(output_path), recursive = TRUE, showWarnings = FALSE)
jsonlite::write_json(benchmarks, output_path, auto_unbox = TRUE, pretty = TRUE, null = "null", na = "null", digits = NA)
cat("Wrote", output_path, "\n")
