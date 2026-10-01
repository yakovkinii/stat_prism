args <- commandArgs(trailingOnly = TRUE)
output_path <- if (length(args) >= 1) {
  args[[1]]
} else {
  file.path("tests", "benchmarks", "reliability", "benchmarks", "reliability_r_benchmarks.json")
}

if (!requireNamespace("jsonlite", quietly = TRUE)) {
  stop("Package 'jsonlite' is required. Install with install.packages('jsonlite').", call. = FALSE)
}
if (!requireNamespace("psych", quietly = TRUE)) {
  stop("Package 'psych' is required. Install with install.packages('psych').", call. = FALSE)
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
  bin_c = c(0, 0, 1, 0, 1, 0, 1, 0, 1, 1)
)

ordinal_string_data <- likert_data
colnames(ordinal_string_data) <- c("ord_a", "ord_b", "ord_c", "ord_d")

clean_number <- function(value) {
  if (is.nan(value) || is.na(value)) {
    return(NA_real_)
  }
  as.numeric(value)
}

cronbach_alpha <- function(corr_matrix) {
  k <- ncol(corr_matrix)
  if (k < 2) {
    return(NaN)
  }
  matrix_sum <- sum(corr_matrix)
  if (matrix_sum == 0) {
    return(NaN)
  }
  (k / (k - 1)) * (1 - (sum(diag(corr_matrix)) / matrix_sum))
}

omega_total <- function(corr_matrix) {
  fit <- psych::fa(r = corr_matrix, nfactors = 1, rotate = "none", fm = "minres")
  loadings <- as.numeric(fit$loadings[, 1])
  uniquenesses <- as.numeric(fit$uniquenesses)
  numerator <- sum(loadings) ^ 2
  denominator <- numerator + sum(uniquenesses)
  if (denominator <= 0) {
    return(NaN)
  }
  numerator / denominator
}

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

tau_c_matrix <- function(df) {
  matrix <- diag(1, ncol(df))
  colnames(matrix) <- colnames(df)
  rownames(matrix) <- colnames(df)
  for (i in seq_len(ncol(df))) {
    for (j in seq_len(ncol(df))) {
      if (i <= j) {
        next
      }
      value <- tau_c_pair(df[[i]], df[[j]])
      matrix[i, j] <- value
      matrix[j, i] <- value
    }
  }
  matrix
}

payload_from_corr <- function(df, corr_matrix, include_omega) {
  corr_values <- as.matrix(corr_matrix)
  full_alpha <- cronbach_alpha(corr_values)
  full_omega <- if (include_omega) omega_total(corr_values) else NA_real_
  total_sum <- sum(corr_values)
  row_sums <- rowSums(corr_values)
  items <- list()
  for (i in seq_len(ncol(corr_values))) {
    off_diagonal <- row_sums[[i]] - corr_values[i, i]
    rest_variance <- total_sum - 2 * row_sums[[i]] + corr_values[i, i]
    sub <- corr_values[-i, -i, drop = FALSE]
    items[[i]] <- list(
      name = colnames(df)[[i]],
      item_rest = clean_number(if (rest_variance > 0) off_diagonal / sqrt(rest_variance) else NaN),
      alpha_deleted = clean_number(cronbach_alpha(sub)),
      omega_deleted = clean_number(if (include_omega) omega_total(sub) else NA_real_)
    )
  }
  list(
    error = "",
    scale = list(
      n_items = ncol(df),
      alpha = clean_number(full_alpha),
      omega = clean_number(full_omega)
    ),
    items = items
  )
}

run_case <- function(df, method, include_omega) {
  if (method == "pearson") {
    corr_matrix <- cor(df, method = "pearson")
  } else if (method == "spearman") {
    corr_matrix <- cor(df, method = "spearman")
  } else if (method == "kendall") {
    corr_matrix <- cor(df, method = "kendall")
  } else if (method == "kendall_c") {
    corr_matrix <- tau_c_matrix(df)
  } else if (method == "phi") {
    if (!all(vapply(df, function(col) length(unique(col)) <= 2, logical(1)))) {
      return(list(
        error = "All columns must have at most 2 unique values for the selected correlation type",
        scale = list(n_items = 0, alpha = NA_real_, omega = NA_real_),
        items = list()
      ))
    }
    corr_matrix <- cor(df, method = "pearson")
  } else if (method == "tetrachoric") {
    corr_matrix <- suppressWarnings(psych::tetrachoric(df, correct = 0)$rho)
  } else if (method == "polychoric") {
    corr_matrix <- suppressWarnings(psych::polychoric(df, correct = 0)$rho)
  } else {
    stop(paste("Unknown method", method))
  }
  payload_from_corr(df, corr_matrix, include_omega)
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
    spearman_three_items_no_omega = run_case(likert_data[, c("item_a", "item_b", "item_c")], "spearman", FALSE),
    kendall_three_items_no_omega = run_case(likert_data[, c("item_a", "item_b", "item_c")], "kendall", FALSE),
    kendall_tau_c_three_items_no_omega = run_case(
      likert_data[, c("item_a", "item_b", "item_c")],
      "kendall_c",
      FALSE
    ),
    phi_binary_items_no_omega = run_case(binary_data[, c("bin_a", "bin_b", "bin_c")], "phi", FALSE),
    tetrachoric_binary_items_no_omega = run_case(
      binary_data[, c("bin_a", "bin_b", "bin_c")],
      "tetrachoric",
      FALSE
    ),
    polychoric_likert_items_no_omega = run_case(
      likert_data[, c("item_a", "item_b", "item_c")],
      "polychoric",
      FALSE
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
