args <- commandArgs(trailingOnly = TRUE)
output_path <- if (length(args) >= 1) {
  args[[1]]
} else {
  file.path("tests", "benchmarks", "correlation", "benchmarks", "correlation_r_benchmarks.json")
}

for (pkg in c("jsonlite", "psych", "polycor", "DescTools", "ppcor")) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    stop(sprintf("Package '%s' is required. Install with install.packages('%s').", pkg, pkg), call. = FALSE)
  }
}

likert_data <- data.frame(
  col_a = c(1, 2, 2, 3, 4, 4, 5, 5, 4, 3),
  col_b = c(1, 2, 3, 3, 4, 5, 5, 5, 4, 4),
  col_c = c(2, 2, 3, 3, 4, 4, 5, 5, 5, 4),
  col_d = c(1, 1, 2, 3, 3, 4, 4, 5, 4, 3)
)
binary_data <- data.frame(
  bin_a = c(0, 0, 1, 1, 1, 0, 1, 0, 1, 1),
  bin_b = c(0, 1, 1, 1, 1, 0, 1, 0, 1, 0),
  bin_c = c(0, 0, 1, 0, 1, 0, 1, 0, 1, 1)
)
likert_cols <- c("col_a", "col_b", "col_c", "col_d")
binary_cols <- c("bin_a", "bin_b", "bin_c")
poly_cols <- c("col_a", "col_b", "col_c")

clean_number <- function(v) {
  if (is.null(v) || length(v) == 0 || is.nan(v) || is.na(v)) NA_real_ else as.numeric(v)
}
pair_rp <- function(r, p) list(r = clean_number(r), p = clean_number(p))
pair_r <- function(r) list(r = clean_number(r))
study <- function(pairs) list(error = "", pairs = pairs)

# Lower-triangle pairs (row index > col index), keyed "<row>__<col>" -- matches run.py's layout.
sq_pairs <- function(cols, fn) {
  out <- list()
  for (i in seq_along(cols)) {
    for (j in seq_along(cols)) {
      if (i <= j) next
      out[[paste0(cols[i], "__", cols[j])]] <- fn(cols[i], cols[j])
    }
  }
  out
}
cross_pairs <- function(rows, cols, fn) {
  out <- list()
  for (r in rows) for (c in cols) out[[paste0(r, "__", c)]] <- fn(r, c)
  out
}

# cor.test (base R) reproduces StatPrism's (scipy) r and p for pearson/spearman/kendall, including the
# t-approximation scipy uses for Spearman p and the tau-b z-test for Kendall.
cortest_rp <- function(df, method) {
  function(x, y) {
    ct <- suppressWarnings(cor.test(df[[x]], df[[y]], method = method))
    pair_rp(ct$estimate, ct$p.value)
  }
}

# Kendall tau-c: DescTools for the coefficient, cor.test(kendall) for the p-value (scipy reports the
# tau-b test p for tau-c, which cor.test(kendall) reproduces).
tauc_fn <- function(x, y) {
  r <- DescTools::StuartTauC(likert_data[[x]], likert_data[[y]])
  p <- suppressWarnings(cor.test(likert_data[[x]], likert_data[[y]], method = "kendall"))$p.value
  pair_rp(r, p)
}

# Phi: Pearson r on the 0/1 items (= phi) and the uncorrected chi-square p (StatPrism uses no Yates).
phi_fn <- function(x, y) {
  r <- cor(binary_data[[x]], binary_data[[y]], method = "pearson")
  p <- suppressWarnings(chisq.test(table(binary_data[[x]], binary_data[[y]]), correct = FALSE))$p.value
  pair_rp(r, p)
}

# Tetrachoric: polycor ML rho, and a likelihood-ratio p. StatPrism's LR test of rho = 0 (thresholds
# fixed at the marginals) equals the G^2 likelihood-ratio test of independence of the 2x2 table, so
# the p is DescTools::GTest (default, no continuity correction).
tetra_fn <- function(x, y) {
  rho <- suppressWarnings(polycor::polychor(binary_data[[x]], binary_data[[y]], ML = TRUE))
  p <- suppressWarnings(DescTools::GTest(table(binary_data[[x]], binary_data[[y]]))$p.value)
  pair_rp(rho, p)
}

# Polychoric rho: psych raw (no smoothing) -- p has no trusted rho=0 equivalent, so coefficient only.
poly_rho <- suppressWarnings(psych::polychoric(likert_data[, poly_cols], correct = 0, smooth = FALSE)$rho)

# Partial correlations via ppcor::pcor.test -- gives both the partial coefficient and its p-value,
# matching StatPrism's pingouin.partial_corr for Pearson and Spearman.
pcor_fn <- function(controls, method) {
  function(x, y) {
    t <- ppcor::pcor.test(likert_data[[x]], likert_data[[y]], likert_data[, controls, drop = FALSE], method = method)
    pair_rp(t$estimate, t$p.value)
  }
}

benchmarks <- list(
  tolerance = 1e-6,
  generated_by = "tests/benchmarks/correlation/r/generate_correlation_benchmarks.R",
  studies = list(
    pearson_square = study(sq_pairs(likert_cols, cortest_rp(likert_data, "pearson"))),
    spearman_square = study(sq_pairs(likert_cols, cortest_rp(likert_data, "spearman"))),
    kendall_square = study(sq_pairs(likert_cols, cortest_rp(likert_data, "kendall"))),
    kendall_tau_c_square = study(sq_pairs(likert_cols, tauc_fn)),
    phi_square = study(sq_pairs(binary_cols, phi_fn)),
    tetrachoric_square = study(sq_pairs(binary_cols, tetra_fn)),
    polychoric_square = study(sq_pairs(poly_cols, function(x, y) pair_r(poly_rho[x, y]))),
    pearson_partial = study(sq_pairs(c("col_a", "col_b", "col_c"), pcor_fn("col_d", "pearson"))),
    spearman_partial = study(sq_pairs(c("col_a", "col_b", "col_c"), pcor_fn("col_d", "spearman"))),
    pearson_cross = study(cross_pairs(c("col_a", "col_b"), c("col_c", "col_d"), cortest_rp(likert_data, "pearson"))),
    spearman_cross = study(cross_pairs(c("col_a", "col_b"), c("col_c", "col_d"), cortest_rp(likert_data, "spearman"))),
    kendall_cross = study(cross_pairs(c("col_a", "col_b"), c("col_c", "col_d"), cortest_rp(likert_data, "kendall"))),
    kendall_tau_c_cross = study(cross_pairs(c("col_a", "col_b"), c("col_c", "col_d"), tauc_fn)),
    phi_cross = study(cross_pairs(c("bin_a", "bin_b"), c("bin_c"), phi_fn)),
    tetrachoric_cross = study(cross_pairs(c("bin_a", "bin_b"), c("bin_c"), tetra_fn)),
    polychoric_cross = study(cross_pairs(c("col_a", "col_b"), c("col_c"), function(x, y) pair_r(poly_rho[x, y]))),
    spearman_partial_cross = study(cross_pairs(c("col_a", "col_b"), c("col_c"), pcor_fn("col_d", "spearman"))),
    pearson_partial_cross = study(cross_pairs(c("col_a", "col_b"), c("col_c"), pcor_fn("col_d", "pearson")))
  )
)

dir.create(dirname(output_path), recursive = TRUE, showWarnings = FALSE)
jsonlite::write_json(benchmarks, output_path, auto_unbox = TRUE, pretty = TRUE, null = "null", na = "null", digits = NA)
cat("Wrote", output_path, "\n")
