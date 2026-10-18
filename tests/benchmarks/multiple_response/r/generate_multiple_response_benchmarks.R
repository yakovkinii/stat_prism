args <- commandArgs(trailingOnly = TRUE)
output_path <- if (length(args) >= 1) {
  args[[1]]
} else {
  file.path("tests", "benchmarks", "multiple_response", "benchmarks", "multiple_response_r_benchmarks.json")
}

for (pkg in c("jsonlite")) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    stop(sprintf("Package '%s' is required. Install with install.packages('%s').", pkg, pkg), call. = FALSE)
  }
}

num <- function(v) as.numeric(v)

# 0/1 indicator columns mirror tests/benchmarks/multiple_response/cases.py.
m <- cbind(
  opt_a = c(1, 0, 1, 1, 0, 1, 0, 1, 1, 0),
  opt_b = c(0, 1, 1, 0, 1, 1, 1, 0, 0, 1),
  opt_c = c(1, 1, 0, 0, 0, 1, 0, 1, 0, 0)
)

counts <- colSums(m != 0)
total_selections <- sum(counts)
n_cases <- sum(rowSums(m != 0) > 0) # respondents with at least one selection

options <- list()
for (nm in colnames(m)) {
  options[[nm]] <- list(
    count = num(counts[[nm]]),
    pct_responses = num(100 * counts[[nm]] / total_selections),
    pct_cases = num(100 * counts[[nm]] / n_cases)
  )
}

benchmarks <- list(
  tolerance = 1e-6,
  generated_by = "tests/benchmarks/multiple_response/r/generate_multiple_response_benchmarks.R",
  studies = list(
    frequencies = list(
      error = "", options = options,
      total_selections = num(total_selections), n_cases = num(n_cases)
    )
  )
)

dir.create(dirname(output_path), recursive = TRUE, showWarnings = FALSE)
jsonlite::write_json(benchmarks, output_path, auto_unbox = TRUE, pretty = TRUE, null = "null", na = "null", digits = NA)
cat("Wrote", output_path, "\n")
