args <- commandArgs(trailingOnly = TRUE)
output_path <- if (length(args) >= 1) {
  args[[1]]
} else {
  file.path("tests", "benchmarks", "contingency", "benchmarks", "contingency_r_benchmarks.json")
}

for (pkg in c("jsonlite")) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    stop(sprintf("Package '%s' is required. Install with install.packages('%s').", pkg, pkg), call. = FALSE)
  }
}

num <- function(v) as.numeric(v)

# A named list keyed by the vector's names (as.numeric alone would strip them, giving a JSON array
# where StatPrism emits a label-keyed object).
named_list <- function(v) {
  out <- as.list(as.numeric(v))
  names(out) <- names(v)
  out
}

# Count matrices mirror tests/benchmarks/contingency/cases.py (rows = v1 categories, cols = v2).
tab_2x3 <- matrix(c(20, 5, 10, 5, 20, 10), nrow = 2, byrow = TRUE,
                  dimnames = list(c("r1", "r2"), c("c1", "c2", "c3")))
tab_2x2 <- matrix(c(8, 2, 1, 9), nrow = 2, byrow = TRUE,
                  dimnames = list(c("r1", "r2"), c("c1", "c2")))
sq_2x2 <- matrix(c(30, 20, 10, 40), nrow = 2, byrow = TRUE,
                 dimnames = list(c("a", "b"), c("a", "b")))
sq_2x2_small <- matrix(c(20, 3, 6, 25), nrow = 2, byrow = TRUE,
                       dimnames = list(c("a", "b"), c("a", "b")))
sq_3x3 <- matrix(c(10, 6, 2, 3, 12, 5, 1, 4, 15), nrow = 3, byrow = TRUE,
                 dimnames = list(c("a", "b", "c"), c("a", "b", "c")))

# Nested named list {rowlabel: {collabel: value}} so the JSON matches the keyed supplement.
nest <- function(m) {
  out <- list()
  for (r in rownames(m)) {
    row <- list()
    for (cc in colnames(m)) row[[cc]] <- num(m[r, cc])
    out[[r]] <- row
  }
  out
}

cramer_v <- function(chi2, m) num(sqrt(chi2 / sum(m) / (min(dim(m)) - 1)))

counts <- function() {
  list(
    error = "", counts = nest(tab_2x3),
    row_totals = named_list(rowSums(tab_2x3)),
    col_totals = named_list(colSums(tab_2x3)),
    grand_total = num(sum(tab_2x3))
  )
}

percent <- function(mode) {
  m <- tab_2x3
  n <- sum(m)
  rt <- rowSums(m)
  cl <- colSums(m)
  if (mode == "Row %") {
    inner <- m / rt * 100
    right <- setNames(rep(100, nrow(m)), rownames(m))
    bottom <- cl / n * 100
  } else if (mode == "Column %") {
    inner <- sweep(m, 2, cl, "/") * 100
    right <- rt / n * 100
    bottom <- setNames(rep(100, ncol(m)), colnames(m))
  } else { # Total %
    inner <- m / n * 100
    right <- rt / n * 100
    bottom <- cl / n * 100
  }
  list(
    error = "", mode = mode, inner = nest(inner),
    right_margin = named_list(right), bottom_margin = named_list(bottom)
  )
}

chi2_study <- function(m, correction, fisher) {
  ht <- suppressWarnings(chisq.test(m, correct = correction))
  out <- list(
    error = "", chi2 = num(ht$statistic), n = num(sum(m)), dof = num(ht$parameter),
    p = num(ht$p.value), cramer_v = cramer_v(num(ht$statistic), m)
  )
  if (fisher) {
    ft <- fisher.test(m)
    # scipy.fisher_exact returns the UNCONDITIONAL (sample) odds ratio ad/bc, not R's conditional MLE.
    out$fisher_odds <- num((m[1, 1] * m[2, 2]) / (m[1, 2] * m[2, 1]))
    out$fisher_p <- num(ft$p.value)
  }
  out
}

residuals_study <- function() {
  # chisq.test()$stdres are the adjusted standardized (Agresti/Haberman) residuals.
  ht <- suppressWarnings(chisq.test(tab_2x3, correct = FALSE))
  list(error = "", residuals = nest(ht$stdres))
}

mcnemar_study <- function(m, correction) {
  # For 2x2 with >= 25 discordant pairs statsmodels uses the chi-square McNemar (matching
  # mcnemar.test); for k>2 R's mcnemar.test computes Bowker's symmetry test (correction ignored).
  ht <- mcnemar.test(m, correct = correction)
  list(error = "", stat = num(ht$statistic), df = num(ht$parameter), p = num(ht$p.value))
}

mcnemar_exact_study <- function(m) {
  # statsmodels' EXACT McNemar (< 25 discordant): statistic = min(b, c), p = two-sided binomial on the
  # discordant pairs; StatPrism reports df = 1. binom.test gives the same two-sided exact p at 0.5.
  b <- m[1, 2]
  c <- m[2, 1]
  list(error = "", stat = num(min(b, c)), df = 1, p = num(binom.test(b, b + c, 0.5)$p.value))
}

benchmarks <- list(
  tolerance = 1e-6,
  generated_by = "tests/benchmarks/contingency/r/generate_contingency_benchmarks.R",
  studies = list(
    counts = counts(),
    percent_row = percent("Row %"),
    percent_col = percent("Column %"),
    percent_total = percent("Total %"),
    chi2_2x3 = chi2_study(tab_2x3, FALSE, FALSE),
    residuals = residuals_study(),
    chi2_2x2_fisher = chi2_study(tab_2x2, TRUE, TRUE),
    mcnemar_2x2 = mcnemar_study(sq_2x2, TRUE),
    mcnemar_exact = mcnemar_exact_study(sq_2x2_small),
    bowker_3x3 = mcnemar_study(sq_3x3, FALSE)
  )
)

dir.create(dirname(output_path), recursive = TRUE, showWarnings = FALSE)
jsonlite::write_json(benchmarks, output_path, auto_unbox = TRUE, pretty = TRUE, null = "null", na = "null", digits = NA)
cat("Wrote", output_path, "\n")
