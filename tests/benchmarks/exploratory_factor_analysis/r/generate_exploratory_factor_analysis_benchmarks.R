args <- commandArgs(trailingOnly = TRUE)
output_path <- if (length(args) >= 1) {
  args[[1]]
} else {
  file.path("tests", "benchmarks", "exploratory_factor_analysis", "benchmarks",
            "exploratory_factor_analysis_r_benchmarks.json")
}

for (pkg in c("jsonlite", "psych", "GPArotation")) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    stop(sprintf("Package '%s' is required. Install with install.packages('%s').", pkg, pkg), call. = FALSE)
  }
}

num <- function(v) as.numeric(v)
data_dir <- file.path(dirname(dirname(output_path)), "data")

X <- as.matrix(read.csv(file.path(data_dir, "efa_data.csv"), stringsAsFactors = FALSE))
R <- cor(X)
n <- nrow(X)

# Canonicalise sign + factor order the same way run.py does.
align <- function(L) {
  L <- as.matrix(L)
  for (j in seq_len(ncol(L))) {
    col <- L[, j]
    if (col[which.max(abs(col))] < 0) L[, j] <- -col
  }
  L[, order(-colSums(L^2)), drop = FALSE]
}
rows <- function(L) lapply(seq_len(nrow(L)), function(i) num(L[i, ]))

diagnostics <- function(rho, n_obs) {
  kmo <- psych::KMO(rho)
  bart <- psych::cortest.bartlett(rho, n = n_obs)
  msa <- as.list(num(kmo$MSAi))
  names(msa) <- colnames(rho)
  list(error = "", kmo = num(kmo$MSA), msa = msa,
       bartlett_chi2 = num(bart$chisq), bartlett_df = num(bart$df), bartlett_p = num(bart$p.value))
}

eigenvalues <- function(rho) {
  ev <- sort(eigen(rho)$values, decreasing = TRUE)
  vp <- ev / sum(ev) * 100
  list(error = "", eigenvalues = num(ev), variance_pct = num(vp),
       cumulative_pct = num(cumsum(vp)), n_kaiser = num(sum(ev > 1)))
}

# psych::fa handles these rotate names directly; quartimin goes through GPArotation.
PSYCH_ROTATIONS <- c("none", "varimax", "quartimax", "equamax", "promax", "oblimin")

fa_rotated <- function(rho, n_obs, fm, rotate_name) {
  tryCatch({
    if (rotate_name %in% PSYCH_ROTATIONS) {
      psych::fa(r = rho, nfactors = 2, n.obs = n_obs, fm = fm, rotate = rotate_name)
    } else {
      f0 <- psych::fa(r = rho, nfactors = 2, n.obs = n_obs, fm = fm, rotate = "none")
      rot <- getExportedValue("GPArotation", rotate_name)(unclass(f0$loadings))
      f0$loadings <- rot$loadings
      f0$Phi <- rot$Phi
      f0
    }
  }, error = function(e) NULL)
}

loadings_study <- function(rho, n_obs, fm, rotate_name) {
  f <- fa_rotated(rho, n_obs, fm, rotate_name)
  if (is.null(f)) {
    return(list(error = "", loadings = rows(matrix(NaN, nrow(rho), 2)),
                communalities = num(rep(NaN, nrow(rho))), uniquenesses = num(rep(NaN, nrow(rho)))))
  }
  L <- align(unclass(f$loadings))
  list(error = "", loadings = rows(L), communalities = num(f$communality), uniquenesses = num(f$uniquenesses))
}

phi_study <- function(rotate_name) {
  f <- fa_rotated(R, n, "minres", rotate_name)
  phi <- if (!is.null(f) && !is.null(f$Phi)) f$Phi else matrix(NaN, 2, 2)
  list(error = "", phi = lapply(seq_len(nrow(phi)), function(i) num(phi[i, ])))
}

structure_study <- function(rotate_name) {
  f <- fa_rotated(R, n, "minres", rotate_name)
  if (is.null(f) || is.null(f$Structure)) {
    S <- matrix(NaN, nrow(R), 2)
  } else {
    S <- align(unclass(f$Structure))
  }
  list(error = "", structure = rows(S))
}

# Polychoric path: diagnostics / eigenvalues / unrotated loadings from the polychoric matrix.
likert <- read.csv(file.path(data_dir, "efa_likert_data.csv"), stringsAsFactors = FALSE)
rho_poly <- suppressWarnings(psych::polychoric(likert)$rho)
n_poly <- nrow(likert)

benchmarks <- list(
  tolerance = 1e-6,
  generated_by = "tests/benchmarks/exploratory_factor_analysis/r/generate_exploratory_factor_analysis_benchmarks.R",
  studies = list(
    diagnostics = diagnostics(R, n),
    eigenvalues = eigenvalues(R),
    loadings_unrotated = loadings_study(R, n, "minres", "none"),
    loadings_ml = loadings_study(R, n, "ml", "none"),
    # factor_analyzer's "principal" method is principal COMPONENTS -> the trusted analog is
    # psych::principal (not fa(fm="pa"), which is iterated principal-axis factoring).
    loadings_principal = {
      pc <- psych::principal(R, nfactors = 2, rotate = "none")
      Lp <- align(unclass(pc$loadings))
      list(error = "", loadings = rows(Lp), communalities = num(pc$communality),
           uniquenesses = num(pc$uniquenesses))
    },
    loadings_varimax = loadings_study(R, n, "minres", "varimax"),
    loadings_quartimax = loadings_study(R, n, "minres", "quartimax"),
    loadings_equamax = loadings_study(R, n, "minres", "equamax"),
    loadings_promax = loadings_study(R, n, "minres", "promax"),
    loadings_oblimin = loadings_study(R, n, "minres", "oblimin"),
    loadings_quartimin = loadings_study(R, n, "minres", "quartimin"),
    phi_promax = phi_study("promax"),
    phi_oblimin = phi_study("oblimin"),
    structure_promax = structure_study("promax"),
    structure_oblimin = structure_study("oblimin"),
    diagnostics_poly = diagnostics(rho_poly, n_poly),
    eigenvalues_poly = eigenvalues(rho_poly),
    loadings_poly = loadings_study(rho_poly, n_poly, "minres", "none")
  )
)

dir.create(dirname(output_path), recursive = TRUE, showWarnings = FALSE)
jsonlite::write_json(benchmarks, output_path, auto_unbox = TRUE, pretty = TRUE, null = "null", na = "null", digits = NA)
cat("Wrote", output_path, "\n")
