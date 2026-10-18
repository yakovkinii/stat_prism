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

# Standardized loadings (items x factors, 0 where not estimated -- matching semopy's layout) and the
# F1~~F2 factor correlation, from any fitted lavaan model.
loadings_phi <- function(fit) {
  std <- lavaan::standardizedSolution(fit)
  L <- matrix(0, nrow = length(cols), ncol = length(facs), dimnames = list(cols, facs))
  load_rows <- std[std$op == "=~", ]
  for (r in seq_len(nrow(load_rows))) {
    L[load_rows$rhs[r], load_rows$lhs[r]] <- load_rows$est.std[r]
  }
  cor_row <- std[std$op == "~~" & std$lhs == "F1" & std$rhs == "F2", ]
  r12 <- if (nrow(cor_row) > 0) num(cor_row$est.std[1]) else 0
  list(
    loadings = list(error = "", std_loadings = lapply(seq_len(nrow(L)), function(i) num(L[i, ]))),
    phi = list(error = "", phi = list(c(1, r12), c(r12, 1)))
  )
}

# fit / loadings / phi from one fitted model. For WLSMV the robust (*.scaled) fit indices are the
# ones that correspond to StatPrism's mean-and-variance-adjusted (SB) values.
build_studies <- function(df, estimator) {
  # StatPrism's DWLS uses the Satorra-Bentler MEAN-AND-VARIANCE adjustment (fractional df); lavaan's
  # default WLSMV is scaled.shifted (integer df), so request mean.var.adjusted to match.
  fit <- if (estimator == "WLSMV") {
    lavaan::cfa(model, data = df, estimator = "DWLS", se = "robust.sem", test = "mean.var.adjusted")
  } else {
    lavaan::cfa(model, data = df, estimator = estimator)
  }
  suffix <- if (estimator == "WLSMV") ".scaled" else ""
  fm <- lavaan::fitMeasures(fit, c(
    paste0("chisq", suffix), paste0("df", suffix), paste0("pvalue", suffix),
    paste0("rmsea", suffix), paste0("cfi", suffix), paste0("tli", suffix), "srmr_bentler"
  ))
  lp <- loadings_phi(fit)
  list(
    fit = list(
      error = "", chi2 = num(fm[[paste0("chisq", suffix)]]), df = num(fm[[paste0("df", suffix)]]),
      p = num(fm[[paste0("pvalue", suffix)]]), rmsea = num(fm[[paste0("rmsea", suffix)]]),
      cfi = num(fm[[paste0("cfi", suffix)]]), tli = num(fm[[paste0("tli", suffix)]]),
      srmr = num(fm[["srmr_bentler"]])
    ),
    loadings = lp$loadings,
    phi = lp$phi
  )
}

ml_df <- read.csv(file.path(data_dir, "cfa_data.csv"), stringsAsFactors = FALSE)
ml <- build_studies(ml_df, "ML")
# Orthogonal model (factor covariance fixed to 0).
orthogonal <- loadings_phi(lavaan::cfa(model, data = ml_df, orthogonal = TRUE))
# semopy's DWLS is fit on the standardized codes (not polychoric); lavaan WLSMV on the same values
# (treated as continuous, i.e. no `ordered=`) is the closest trusted reference.
dwls_df <- read.csv(file.path(data_dir, "cfa_dwls_data.csv"), stringsAsFactors = FALSE)
dwls <- build_studies(dwls_df, "WLSMV")
# Polychoric ULS: the ordinal estimator. lavaan estimator="ULS" with `ordered=` uses polychoric
# correlations + ULS -- the trusted match for StatPrism's new polychoric-ULS (loadings / phi only;
# fit indices are naive on both sides and not benchmarked).
uls <- loadings_phi(lavaan::cfa(model, data = dwls_df, ordered = cols, estimator = "ULS"))

# Second-order factor: a general factor G over the three first-order factors.
so_model <- "F1 =~ v1 + v2 + v3
             F2 =~ v4 + v5 + v6
             F3 =~ v7 + v8 + v9
             G  =~ F1 + F2 + F3"
so_df <- read.csv(file.path(data_dir, "cfa_3factor_data.csv"), stringsAsFactors = FALSE)
so_std <- lavaan::standardizedSolution(lavaan::cfa(so_model, data = so_df))
so_rows <- so_std[so_std$op == "=~" & so_std$lhs == "G", ]
so_loadings <- as.list(num(so_rows$est.std))
names(so_loadings) <- so_rows$rhs  # F1, F2, F3

# Applied cross-loading: v3 also loads on F2.
cross <- loadings_phi(lavaan::cfa("F1 =~ v1 + v2 + v3\nF2 =~ v4 + v5 + v6 + v3", data = ml_df))

# Freed residual correlation v1 ~~ v2.
resid_fit <- lavaan::cfa("F1 =~ v1 + v2 + v3\nF2 =~ v4 + v5 + v6\nv1 ~~ v2", data = ml_df)
resid_fm <- lavaan::fitMeasures(resid_fit, c("chisq", "df", "pvalue", "rmsea", "cfi", "tli", "srmr_bentler"))

benchmarks <- list(
  tolerance = 1e-6,
  generated_by = "tests/benchmarks/confirmatory_factor_analysis/r/generate_confirmatory_factor_analysis_benchmarks.R",
  studies = list(
    cfa_fit = ml$fit,
    cfa_loadings = ml$loadings,
    cfa_phi = ml$phi,
    cfa_dwls_fit = dwls$fit,
    cfa_dwls_loadings = dwls$loadings,
    cfa_dwls_phi = dwls$phi,
    cfa_uls_loadings = uls$loadings,
    cfa_uls_phi = uls$phi,
    cfa_orthogonal_loadings = orthogonal$loadings,
    cfa_second_order = list(error = "", loadings = so_loadings),
    cfa_cross_loading_loadings = cross$loadings,
    cfa_residual_fit = list(
      error = "", chi2 = num(resid_fm[["chisq"]]), df = num(resid_fm[["df"]]), p = num(resid_fm[["pvalue"]]),
      rmsea = num(resid_fm[["rmsea"]]), cfi = num(resid_fm[["cfi"]]), tli = num(resid_fm[["tli"]]),
      srmr = num(resid_fm[["srmr_bentler"]])
    )
  )
)

dir.create(dirname(output_path), recursive = TRUE, showWarnings = FALSE)
jsonlite::write_json(benchmarks, output_path, auto_unbox = TRUE, pretty = TRUE, null = "null", na = "null", digits = NA)
cat("Wrote", output_path, "\n")
