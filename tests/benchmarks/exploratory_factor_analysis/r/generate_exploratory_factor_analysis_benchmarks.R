args <- commandArgs(trailingOnly = TRUE)
output_path <- if (length(args) >= 1) {
  args[[1]]
} else {
  file.path("tests", "benchmarks", "exploratory_factor_analysis", "benchmarks",
            "exploratory_factor_analysis_r_benchmarks.json")
}

for (pkg in c("jsonlite", "psych")) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    stop(sprintf("Package '%s' is required. Install with install.packages('%s').", pkg, pkg), call. = FALSE)
  }
}

num <- function(v) as.numeric(v)

data_path <- file.path(dirname(dirname(output_path)), "data", "efa_data.csv")
df <- read.csv(data_path, stringsAsFactors = FALSE)
X <- as.matrix(df)
R <- cor(X)
n <- nrow(X)
cols <- colnames(X)

# Canonicalise sign + factor order the same way run.py does.
align <- function(L) {
  L <- as.matrix(L)
  for (j in seq_len(ncol(L))) {
    col <- L[, j]
    if (col[which.max(abs(col))] < 0) L[, j] <- -col
  }
  ord <- order(-colSums(L^2))
  L[, ord, drop = FALSE]
}

diagnostics <- function() {
  kmo <- psych::KMO(R)
  bart <- psych::cortest.bartlett(R, n = n)
  msa <- as.list(num(kmo$MSAi))
  names(msa) <- cols
  list(
    error = "", kmo = num(kmo$MSA), msa = msa,
    bartlett_chi2 = num(bart$chisq), bartlett_df = num(bart$df), bartlett_p = num(bart$p.value)
  )
}

eigenvalues <- function() {
  ev <- sort(eigen(R)$values, decreasing = TRUE)
  vp <- ev / sum(ev) * 100
  list(
    error = "", eigenvalues = num(ev), variance_pct = num(vp),
    cumulative_pct = num(cumsum(vp)), n_kaiser = num(sum(ev > 1))
  )
}

loadings_unrotated <- function() {
  f <- psych::fa(r = R, nfactors = 2, n.obs = n, fm = "minres", rotate = "none")
  L <- align(unclass(f$loadings))
  rows <- lapply(seq_len(nrow(L)), function(i) num(L[i, ]))
  list(
    error = "", loadings = rows,
    communalities = num(f$communality), uniquenesses = num(f$uniquenesses)
  )
}

benchmarks <- list(
  tolerance = 1e-6,
  generated_by = "tests/benchmarks/exploratory_factor_analysis/r/generate_exploratory_factor_analysis_benchmarks.R",
  studies = list(
    diagnostics = diagnostics(),
    eigenvalues = eigenvalues(),
    loadings_unrotated = loadings_unrotated()
  )
)

dir.create(dirname(output_path), recursive = TRUE, showWarnings = FALSE)
jsonlite::write_json(benchmarks, output_path, auto_unbox = TRUE, pretty = TRUE, null = "null", na = "null", digits = NA)
cat("Wrote", output_path, "\n")
