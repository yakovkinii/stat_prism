args <- commandArgs(trailingOnly = TRUE)
output_path <- if (length(args) >= 1) {
  args[[1]]
} else {
  file.path("tests", "benchmarks", "power_analysis", "benchmarks", "power_analysis_r_benchmarks.json")
}

for (pkg in c("jsonlite", "pwr")) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    stop(sprintf("Package '%s' is required. Install with install.packages('%s').", pkg, pkg), call. = FALSE)
  }
}

num <- function(v) as.numeric(v)

# Each study returns only the fields benchmarked for that case (see cases.py) so the payloads match
# key-for-key. Sample-size solves ceil to whole observations, exactly as StatPrism does.

two_sample_n <- function(alt) {
  r <- pwr::pwr.t.test(d = 0.5, power = 0.8, sig.level = 0.05, type = "two.sample", alternative = alt)
  npg <- ceiling(r$n)
  list(error = "", solved_value = num(npg), n_total = num(npg * 2), n_per_group = num(npg))
}

two_sample_power <- function() {
  r <- pwr::pwr.t.test(n = 30, d = 0.5, sig.level = 0.05, type = "two.sample", alternative = "two.sided")
  list(error = "", solved_value = num(r$power))
}

two_sample_effect <- function() {
  r <- pwr::pwr.t.test(n = 30, power = 0.8, sig.level = 0.05, type = "two.sample", alternative = "two.sided")
  list(error = "", solved_value = num(r$d))
}

paired_power <- function() {
  # StatPrism routes paired / one-sample to statsmodels TTestPower (df = n - 1, ncp = d*sqrt(n)).
  r <- pwr::pwr.t.test(n = 30, d = 0.5, sig.level = 0.05, type = "one.sample", alternative = "two.sided")
  list(error = "", solved_value = num(r$power))
}

anova_n <- function() {
  r <- pwr::pwr.anova.test(k = 4, f = 0.25, power = 0.8, sig.level = 0.05)
  ntot <- ceiling(r$n * 4)
  npg <- ceiling(r$n)
  list(error = "", solved_value = num(ntot), n_total = num(ntot), n_per_group = num(npg))
}

anova_power <- function() {
  # StatPrism passes total N (= 80) to statsmodels; pwr takes per-group n = 80 / k.
  r <- pwr::pwr.anova.test(k = 4, n = 80 / 4, f = 0.25, sig.level = 0.05)
  list(error = "", solved_value = num(r$power))
}

corr_power <- function() {
  r <- pwr::pwr.r.test(n = 50, r = 0.3, sig.level = 0.05, alternative = "two.sided")
  list(error = "", solved_value = num(r$power))
}

corr_n <- function() {
  r <- pwr::pwr.r.test(r = 0.3, power = 0.8, sig.level = 0.05, alternative = "two.sided")
  npg <- ceiling(r$n)
  list(error = "", solved_value = num(npg), n_per_group = num(npg))
}

benchmarks <- list(
  tolerance = 1e-6,
  generated_by = "tests/benchmarks/power_analysis/r/generate_power_analysis_benchmarks.R",
  studies = list(
    two_sample_n = two_sample_n("two.sided"),
    two_sample_n_one_sided = two_sample_n("greater"),
    two_sample_power = two_sample_power(),
    two_sample_effect = two_sample_effect(),
    paired_power = paired_power(),
    anova_n = anova_n(),
    anova_power = anova_power(),
    corr_power = corr_power(),
    corr_n = corr_n()
  )
)

dir.create(dirname(output_path), recursive = TRUE, showWarnings = FALSE)
jsonlite::write_json(benchmarks, output_path, auto_unbox = TRUE, pretty = TRUE, null = "null", na = "null", digits = NA)
cat("Wrote", output_path, "\n")
