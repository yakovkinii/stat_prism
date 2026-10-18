args <- commandArgs(trailingOnly = TRUE)
output_path <- if (length(args) >= 1) {
  args[[1]]
} else {
  file.path("tests", "benchmarks", "confirmatory_factor_analysis", "benchmarks",
            "confirmatory_factor_analysis_r_benchmarks.json")
}

for (pkg in c("jsonlite", "lavaan")) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    stop(sprintf("Package '%s' is required. Install with install.packages('%s').", pkg, pkg), call. = FALSE)
  }
}

num <- function(v) as.numeric(v)
data_dir <- file.path(dirname(dirname(output_path)), "data")

model <- "F1 =~ v1 + v2 + v3
          F2 =~ v4 + v5 + v6"
cols <- c("v1", "v2", "v3", "v4", "v5", "v6")
facs <- c("F1", "F2")

# Three studies (fit / loadings / phi) from one fitted model. For WLSMV the robust (*.scaled) fit
# indices are the ones that correspond to StatPrism's mean-and-variance-adjusted (SB) values.
build_studies <- function(df, estimator) {
  fit <- lavaan::cfa(model, data = df, estimator = estimator)
  suffix <- if (estimator == "WLSMV") ".scaled" else ""
  fm <- lavaan::fitMeasures(fit, c(
    paste0("chisq", suffix), paste0("df", suffix), paste0("pvalue", suffix),
    paste0("rmsea", suffix), paste0("cfi", suffix), paste0("tli", suffix), "srmr_bentler"
  ))
  std <- lavaan::standardizedSolution(fit)

  # Standardized loadings matrix (items x factors), 0 where not estimated -- matching semopy's layout.
  L <- matrix(0, nrow = length(cols), ncol = length(facs), dimnames = list(cols, facs))
  load_rows <- std[std$op == "=~", ]
  for (r in seq_len(nrow(load_rows))) {
    L[load_rows$rhs[r], load_rows$lhs[r]] <- load_rows$est.std[r]
  }
  loadings <- lapply(seq_len(nrow(L)), function(i) num(L[i, ]))

  cor_row <- std[std$op == "~~" & std$lhs == "F1" & std$rhs == "F2", ]
  r12 <- if (nrow(cor_row) > 0) num(cor_row$est.std[1]) else 0

  list(
    fit = list(
      error = "", chi2 = num(fm[[paste0("chisq", suffix)]]), df = num(fm[[paste0("df", suffix)]]),
      p = num(fm[[paste0("pvalue", suffix)]]), rmsea = num(fm[[paste0("rmsea", suffix)]]),
      cfi = num(fm[[paste0("cfi", suffix)]]), tli = num(fm[[paste0("tli", suffix)]]),
      srmr = num(fm[["srmr_bentler"]])
    ),
    loadings = list(error = "", std_loadings = loadings),
    phi = list(error = "", phi = list(c(1, r12), c(r12, 1)))
  )
}

ml <- build_studies(read.csv(file.path(data_dir, "cfa_data.csv"), stringsAsFactors = FALSE), "ML")
# semopy's DWLS is fit on the standardized codes (not polychoric); lavaan WLSMV on the same values
# (treated as continuous, i.e. no `ordered=`) is the closest trusted reference.
dwls <- build_studies(read.csv(file.path(data_dir, "cfa_dwls_data.csv"), stringsAsFactors = FALSE), "WLSMV")

benchmarks <- list(
  tolerance = 1e-6,
  generated_by = "tests/benchmarks/confirmatory_factor_analysis/r/generate_confirmatory_factor_analysis_benchmarks.R",
  studies = list(
    cfa_fit = ml$fit,
    cfa_loadings = ml$loadings,
    cfa_phi = ml$phi,
    cfa_dwls_fit = dwls$fit,
    cfa_dwls_loadings = dwls$loadings,
    cfa_dwls_phi = dwls$phi
  )
)

dir.create(dirname(output_path), recursive = TRUE, showWarnings = FALSE)
jsonlite::write_json(benchmarks, output_path, auto_unbox = TRUE, pretty = TRUE, null = "null", na = "null", digits = NA)
cat("Wrote", output_path, "\n")
