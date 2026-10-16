args <- commandArgs(trailingOnly = TRUE)
output_path <- if (length(args) >= 1) {
  args[[1]]
} else {
  file.path("tests", "benchmarks", "correlation", "benchmarks", "correlation_r_benchmarks.json")
}

if (!requireNamespace("jsonlite", quietly = TRUE)) {
  stop("Package 'jsonlite' is required. Install with install.packages('jsonlite').", call. = FALSE)
}
if (!requireNamespace("psych", quietly = TRUE)) {
  stop("Package 'psych' is required. Install with install.packages('psych').", call. = FALSE)
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

clean_number <- function(value) {
  if (is.null(value) || length(value) == 0 || is.nan(value) || is.na(value)) {
    return(NA_real_)
  }
  as.numeric(value)
}

# Stuart's tau-c for one pair (matches scipy kendalltau(variant="c")).
tau_c_pair <- function(x, y) {
  valid <- data.frame(x = x, y = y)
  valid <- valid[complete.cases(valid), ]
  n <- nrow(valid)
  if (n < 2) {
    return(NaN)
  }
  p <- 0
  q <- 0
  for (i in seq_len(n - 1)) {
    for (j in seq.int(i + 1, n)) {
      product <- sign(valid$x[[j]] - valid$x[[i]]) * sign(valid$y[[j]] - valid$y[[i]])
      if (product > 0) {
        p <- p + 1
      } else if (product < 0) {
        q <- q + 1
      }
    }
  }
  m <- min(length(unique(valid$x)), length(unique(valid$y)))
  if (m <= 1) {
    return(NaN)
  }
  2 * m * (p - q) / (n ^ 2 * (m - 1))
}

# Partial correlation of x, y given controls via residualisation (ranks first for Spearman, matching
# pingouin.partial_corr). With no controls this reduces to the plain coefficient.
partial_r <- function(df, x, y, controls, spearman = FALSE) {
  used <- c(x, y, controls)
  d <- df[, used, drop = FALSE]
  d <- d[complete.cases(d), ]
  if (spearman) {
    for (name in used) {
      d[[name]] <- rank(d[[name]])
    }
  }
  if (length(controls) == 0) {
    return(cor(d[[x]], d[[y]], method = "pearson"))
  }
  fx <- resid(lm(reformulate(controls, response = x), data = d))
  fy <- resid(lm(reformulate(controls, response = y), data = d))
  cor(fx, fy, method = "pearson")
}

square_pairs_fun <- function(df, cols, rfun) {
  out <- list()
  for (i in seq_along(cols)) {
    for (j in seq_along(cols)) {
      if (i <= j) {
        next
      }
      out[[paste0(cols[i], "__", cols[j])]] <- clean_number(rfun(df[[cols[i]]], df[[cols[j]]]))
    }
  }
  out
}

square_pairs_matrix <- function(cols, mat) {
  out <- list()
  for (i in seq_along(cols)) {
    for (j in seq_along(cols)) {
      if (i <= j) {
        next
      }
      out[[paste0(cols[i], "__", cols[j])]] <- clean_number(mat[cols[i], cols[j]])
    }
  }
  out
}

partial_square_pairs <- function(df, vars, controls, spearman) {
  out <- list()
  for (i in seq_along(vars)) {
    for (j in seq_along(vars)) {
      if (i <= j) {
        next
      }
      out[[paste0(vars[i], "__", vars[j])]] <- clean_number(partial_r(df, vars[i], vars[j], controls, spearman))
    }
  }
  out
}

cross_pairs_fun <- function(df, rows, cols, rfun) {
  out <- list()
  for (r in rows) {
    for (c in cols) {
      out[[paste0(r, "__", c)]] <- clean_number(rfun(df[[r]], df[[c]]))
    }
  }
  out
}

cross_partial_pairs <- function(df, rows, cols, controls, spearman) {
  out <- list()
  for (r in rows) {
    for (c in cols) {
      out[[paste0(r, "__", c)]] <- clean_number(partial_r(df, r, c, controls, spearman))
    }
  }
  out
}

study <- function(pairs) {
  list(error = "", pairs = pairs)
}

pearson_r <- function(x, y) cor(x, y, method = "pearson")
spearman_r <- function(x, y) cor(x, y, method = "spearman")
kendall_r <- function(x, y) cor(x, y, method = "kendall")

likert_cols <- c("col_a", "col_b", "col_c", "col_d")
binary_cols <- c("bin_a", "bin_b", "bin_c")
poly_cols <- c("col_a", "col_b", "col_c")

# smooth = FALSE: StatPrism's correlation module reports the RAW per-pair latent-correlation MLE and
# does not force the matrix positive-definite, so psych must not smooth either (its default smoothing
# would perturb every entry and the two would no longer be comparing the same quantity).
tetrachoric_rho <- suppressWarnings(psych::tetrachoric(binary_data[, binary_cols], correct = 0, smooth = FALSE)$rho)
polychoric_rho <- suppressWarnings(psych::polychoric(likert_data[, poly_cols], correct = 0, smooth = FALSE)$rho)

benchmarks <- list(
  tolerance = 1e-6,
  generated_by = "tests/benchmarks/correlation/r/generate_correlation_benchmarks.R",
  studies = list(
    pearson_square = study(square_pairs_fun(likert_data, likert_cols, pearson_r)),
    spearman_square = study(square_pairs_fun(likert_data, likert_cols, spearman_r)),
    kendall_square = study(square_pairs_fun(likert_data, likert_cols, kendall_r)),
    kendall_tau_c_square = study(square_pairs_fun(likert_data, likert_cols, tau_c_pair)),
    phi_square = study(square_pairs_fun(binary_data, binary_cols, pearson_r)),
    tetrachoric_square = study(square_pairs_matrix(binary_cols, tetrachoric_rho)),
    polychoric_square = study(square_pairs_matrix(poly_cols, polychoric_rho)),
    pearson_partial = study(partial_square_pairs(likert_data, c("col_a", "col_b", "col_c"), c("col_d"), FALSE)),
    spearman_partial = study(partial_square_pairs(likert_data, c("col_a", "col_b", "col_c"), c("col_d"), TRUE)),
    pearson_cross = study(cross_pairs_fun(likert_data, c("col_a", "col_b"), c("col_c", "col_d"), pearson_r)),
    spearman_partial_cross = study(
      cross_partial_pairs(likert_data, c("col_a", "col_b"), c("col_c"), c("col_d"), TRUE)
    )
  )
)

dir.create(dirname(output_path), recursive = TRUE, showWarnings = FALSE)
jsonlite::write_json(
  benchmarks,
  output_path,
  auto_unbox = TRUE,
  pretty = TRUE,
  null = "null",
  na = "null",
  digits = NA
)
cat("Wrote", output_path, "\n")
