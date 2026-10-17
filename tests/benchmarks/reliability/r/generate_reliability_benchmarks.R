args <- commandArgs(trailingOnly = TRUE)
output_path <- if (length(args) >= 1) {
  args[[1]]
} else {
  file.path("tests", "benchmarks", "reliability", "benchmarks", "reliability_r_benchmarks.json")
}

for (pkg in c("jsonlite", "psych", "DescTools")) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    stop(sprintf("Package '%s' is required. Install with install.packages('%s').", pkg, pkg), call. = FALSE)
  }
}

likert_data <- data.frame(
  item_a = c(1, 2, 2, 3, 4, 4, 5, 5, 4, 3),
  item_b = c(1, 2, 3, 3, 4, 5, 5, 5, 4, 4),
  item_c = c(2, 2, 3, 3, 4, 4, 5, 5, 5, 4),
  item_d = c(1, 1, 2, 3, 3, 4, 4, 5, 4, 3)
)

binary_data <- data.frame(
  bin_a = c(0, 0, 1, 1, 1, 0, 1, 0, 1, 1),
  bin_b = c(0, 1, 1, 1, 1, 0, 1, 0, 1, 0),
  bin_c = c(0, 0, 1, 0, 1, 0, 1, 0, 1, 1),
  bin_d = c(0, 0, 1, 1, 1, 0, 1, 1, 1, 0)
)

ordinal_string_data <- likert_data
colnames(ordinal_string_data) <- c("ord_a", "ord_b", "ord_c", "ord_d")

clean_number <- function(value) {
  if (is.null(value) || length(value) == 0 || is.nan(value) || is.na(value)) NA_real_ else as.numeric(value)
}

# Standardized Cronbach's alpha and McDonald's omega-total come from trusted psych routines, not a
# local re-implementation: psych::alpha(correlation matrix) gives std.alpha, the item-rest r.drop and
# the std.alpha-if-dropped; psych::omega(nfactors = 1, fm = "minres") gives the single-common-factor
# omega-total (matching StatPrism's factor_analyzer fit). Only small pre/post-processing is ours.
omega_total <- function(corr_matrix) {
  suppressWarnings(psych::omega(corr_matrix, nfactors = 1, fm = "minres", plot = FALSE)$omega.tot)
}

tau_c_matrix <- function(df) {
  cols <- colnames(df)
  m <- diag(1, length(cols))
  dimnames(m) <- list(cols, cols)
  for (i in seq_along(cols)) {
    for (j in seq_along(cols)) {
      if (i <= j) next
      value <- DescTools::StuartTauC(df[[cols[i]]], df[[cols[j]]])
      m[i, j] <- value
      m[j, i] <- value
    }
  }
  m
}

payload_from_corr <- function(cols, corr_matrix, include_omega, n_obs) {
  a <- suppressWarnings(psych::alpha(corr_matrix, n.obs = n_obs, check.keys = FALSE))
  r_drop <- a$item.stats$r.drop
  alpha_drop <- a$alpha.drop$std.alpha
  items <- list()
  for (i in seq_along(cols)) {
    omega_deleted <- if (include_omega) omega_total(corr_matrix[-i, -i, drop = FALSE]) else NA_real_
    items[[i]] <- list(
      name = cols[[i]],
      item_rest = clean_number(r_drop[[i]]),
      alpha_deleted = clean_number(alpha_drop[[i]]),
      omega_deleted = clean_number(omega_deleted)
    )
  }
  list(
    error = "",
    scale = list(
      n_items = ncol(corr_matrix),
      alpha = clean_number(a$total$std.alpha),
      omega = clean_number(if (include_omega) omega_total(corr_matrix) else NA_real_)
    ),
    items = items
  )
}

corr_for <- function(df, method) {
  if (method == "pearson") {
    cor(df, method = "pearson")
  } else if (method == "spearman") {
    cor(df, method = "spearman")
  } else if (method == "kendall") {
    cor(df, method = "kendall")
  } else if (method == "kendall_c") {
    tau_c_matrix(df)
  } else if (method == "phi") {
    if (!all(vapply(df, function(col) length(unique(col)) <= 2, logical(1)))) {
      return(NULL)
    }
    cor(df, method = "pearson") # phi == Pearson on 0/1 items
  } else if (method == "tetrachoric") {
    suppressWarnings(psych::tetrachoric(df, correct = 0)$rho) # psych default smoothing, matching StatPrism
  } else if (method == "polychoric") {
    suppressWarnings(psych::polychoric(df, correct = 0)$rho)
  } else {
    stop(paste("Unknown method", method))
  }
}

run_case <- function(df, method, include_omega) {
  corr_matrix <- corr_for(df, method)
  if (is.null(corr_matrix)) {
    return(list(
      error = "All columns must have at most 2 unique values for the selected correlation type",
      scale = list(n_items = 0, alpha = NA_real_, omega = NA_real_),
      items = list()
    ))
  }
  payload_from_corr(colnames(df), corr_matrix, include_omega, nrow(df))
}

benchmarks <- list(
  tolerance = 1e-6,
  generated_by = "tests/benchmarks/reliability/r/generate_reliability_benchmarks.R",
  studies = list(
    pearson_four_items_with_omega = run_case(likert_data[, c("item_a", "item_b", "item_c", "item_d")], "pearson", TRUE),
    pearson_ordinal_string_items_with_omega = run_case(
      ordinal_string_data[, c("ord_a", "ord_b", "ord_c", "ord_d")],
      "pearson",
      TRUE
    ),
    spearman_four_items_with_omega = run_case(likert_data[, c("item_a", "item_b", "item_c", "item_d")], "spearman", TRUE),
    kendall_four_items_with_omega = run_case(likert_data[, c("item_a", "item_b", "item_c", "item_d")], "kendall", TRUE),
    kendall_tau_c_four_items_with_omega = run_case(
      likert_data[, c("item_a", "item_b", "item_c", "item_d")],
      "kendall_c",
      TRUE
    ),
    phi_binary_items_with_omega = run_case(binary_data[, c("bin_a", "bin_b", "bin_c", "bin_d")], "phi", TRUE),
    tetrachoric_binary_items_with_omega = run_case(
      binary_data[, c("bin_a", "bin_b", "bin_c", "bin_d")],
      "tetrachoric",
      TRUE
    ),
    polychoric_likert_items_with_omega = run_case(
      likert_data[, c("item_a", "item_b", "item_c", "item_d")],
      "polychoric",
      TRUE
    )
  )
)

dir.create(dirname(output_path), recursive = TRUE, showWarnings = FALSE)
jsonlite::write_json(benchmarks, output_path, auto_unbox = TRUE, pretty = TRUE, null = "null", na = "null", digits = NA)
cat("Wrote", output_path, "\n")
