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

model <- "F1 =~ v1 + v2 + v3
          F2 =~ v4 + v5 + v6
          F2 ~ F1"
fit <- lavaan::sem(model, data = df)  # ML

fm <- lavaan::fitMeasures(fit, c("chisq", "df", "pvalue", "cfi", "tli", "rmsea"))
std <- lavaan::standardizedSolution(fit)

# Standardized loadings (=~) and the structural regression (~), keyed "<lhs><op><rhs>".
params <- list()
keep <- std[std$op %in% c("=~", "~"), ]
for (r in seq_len(nrow(keep))) {
  key <- paste0(keep$lhs[r], keep$op[r], keep$rhs[r])
  params[[key]] <- num(keep$est.std[r])
}

benchmarks <- list(
  tolerance = 1e-6,
  generated_by = "tests/benchmarks/general_sem/r/generate_general_sem_benchmarks.R",
  studies = list(
    sem_fit = list(
      error = "", chi2 = num(fm[["chisq"]]), df = num(fm[["df"]]), p = num(fm[["pvalue"]]),
      cfi = num(fm[["cfi"]]), tli = num(fm[["tli"]]), rmsea = num(fm[["rmsea"]])
    ),
    sem_params = list(error = "", std = params)
  )
)

dir.create(dirname(output_path), recursive = TRUE, showWarnings = FALSE)
jsonlite::write_json(benchmarks, output_path, auto_unbox = TRUE, pretty = TRUE, null = "null", na = "null", digits = NA)
cat("Wrote", output_path, "\n")
