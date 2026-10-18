args <- commandArgs(trailingOnly = TRUE)
output_path <- if (length(args) >= 1) {
  args[[1]]
} else {
  file.path("tests", "benchmarks", "general_sem", "benchmarks", "general_sem_r_benchmarks.json")
}

for (pkg in c("jsonlite", "lavaan")) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    stop(sprintf("Package '%s' is required. Install with install.packages('%s').", pkg, pkg), call. = FALSE)
  }
}

num <- function(v) as.numeric(v)
data_path <- file.path(dirname(dirname(output_path)), "data", "sem_data.csv")
df <- read.csv(data_path, stringsAsFactors = FALSE)

measurement <- "F1 =~ v1 + v2 + v3\nF2 =~ v4 + v5 + v6\n"

# A covariance (~~) is undirected; sort its two sides so keys compare equal to StatPrism's.
canon <- function(key) {
  if (grepl("~~", key, fixed = TRUE)) {
    return(paste(sort(strsplit(key, "~~", fixed = TRUE)[[1]]), collapse = "~~"))
  }
  key
}

std_params <- function(fit) {
  std <- lavaan::standardizedSolution(fit)
  keep <- std[std$op %in% c("=~", "~") | (std$op == "~~" & std$lhs != std$rhs), ]
  out <- list()
  for (r in seq_len(nrow(keep))) {
    lhs <- keep$lhs[r]; op <- keep$op[r]; rhs <- keep$rhs[r]
    # Match StatPrism's semopy key format: a loading is reported as "indicator ~ factor" (op '~'),
    # a regression as "outcome ~ predictor", a covariance as a sorted "a ~~ b".
    if (op == "=~") {
      key <- paste0(rhs, "~", lhs)
    } else if (op == "~") {
      key <- paste0(lhs, "~", rhs)
    } else {
      key <- canon(paste0(lhs, "~~", rhs))
    }
    out[[key]] <- num(keep$est.std[r])
  }
  out
}

fit_indices <- function(fit, scaled) {
  suffix <- if (scaled) ".scaled" else ""
  fm <- lavaan::fitMeasures(fit, c(
    paste0("chisq", suffix), paste0("df", suffix), paste0("pvalue", suffix),
    paste0("cfi", suffix), paste0("tli", suffix), paste0("rmsea", suffix)
  ))
  list(
    error = "", chi2 = num(fm[[paste0("chisq", suffix)]]), df = num(fm[[paste0("df", suffix)]]),
    p = num(fm[[paste0("pvalue", suffix)]]), cfi = num(fm[[paste0("cfi", suffix)]]),
    tli = num(fm[[paste0("tli", suffix)]]), rmsea = num(fm[[paste0("rmsea", suffix)]])
  )
}

reg_fit <- lavaan::sem(paste0(measurement, "F2 ~ F1"), data = df)             # regression path, ML
cov_fit <- lavaan::sem(paste0(measurement, "F1 ~~ F2"), data = df)            # covariance path, ML
# StatPrism's DWLS uses Satorra-Bentler mean-and-variance adjustment (fractional df); match it with
# test="mean.var.adjusted" rather than lavaan's default WLSMV (scaled.shifted, integer df).
dwls_fit <- lavaan::sem(paste0(measurement, "F2 ~ F1"), data = df,
                        estimator = "DWLS", se = "robust.sem", test = "mean.var.adjusted")

benchmarks <- list(
  tolerance = 1e-6,
  generated_by = "tests/benchmarks/general_sem/r/generate_general_sem_benchmarks.R",
  studies = list(
    sem_fit = fit_indices(reg_fit, FALSE),
    sem_params = list(error = "", std = std_params(reg_fit)),
    sem_covariance = list(error = "", std = std_params(cov_fit)),
    sem_dwls_fit = fit_indices(dwls_fit, TRUE)
  )
)

dir.create(dirname(output_path), recursive = TRUE, showWarnings = FALSE)
jsonlite::write_json(benchmarks, output_path, auto_unbox = TRUE, pretty = TRUE, null = "null", na = "null", digits = NA)
cat("Wrote", output_path, "\n")
