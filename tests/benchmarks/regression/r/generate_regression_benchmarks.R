args <- commandArgs(trailingOnly = TRUE)
output_path <- if (length(args) >= 1) {
  args[[1]]
} else {
  file.path("tests", "benchmarks", "regression", "benchmarks", "regression_r_benchmarks.json")
}

for (pkg in c("jsonlite", "car", "nnet")) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    stop(sprintf("Package '%s' is required. Install with install.packages('%s').", pkg, pkg), call. = FALSE)
  }
}

# The data CSV sits next to the generator's module (regression/data/), the benchmark JSON in
# regression/benchmarks/ -- so the data is one directory up from the output, under data/.
data_path <- file.path(dirname(dirname(output_path)), "data", "regression_data.csv")
df <- read.csv(data_path, stringsAsFactors = FALSE)
n <- nrow(df)

num <- function(v) as.numeric(v)

# ---- Linear (OLS): y ~ x1 + x2 ----
lin <- lm(y ~ x1 + x2, data = df)
lin_s <- summary(lin)

linear_fit <- function() {
  fs <- lin_s$fstatistic
  list(
    error = "", n = num(n), r2 = num(lin_s$r.squared), adj_r2 = num(lin_s$adj.r.squared),
    f = num(fs[["value"]]), df_model = num(fs[["numdf"]]), df_resid = num(fs[["dendf"]]),
    f_p = num(pf(fs[["value"]], fs[["numdf"]], fs[["dendf"]], lower.tail = FALSE))
  )
}

linear_coef <- function() {
  co <- lin_s$coefficients
  sd_y <- sd(df$y)
  rows <- list()
  for (nm in rownames(co)) {
    beta <- if (nm == "(Intercept)") NA else num(co[nm, "Estimate"] * sd(df[[nm]]) / sd_y)
    rows[[length(rows) + 1]] <- list(
      b = num(co[nm, "Estimate"]), se = num(co[nm, "Std. Error"]), beta = beta,
      t = num(co[nm, "t value"]), p = num(co[nm, "Pr(>|t|)"])
    )
  }
  list(error = "", rows = rows)
}

linear_vif <- function() {
  v <- car::vif(lin)
  list(error = "", rows = list(
    list(name = "x1", vif = num(v[["x1"]])),
    list(name = "x2", vif = num(v[["x2"]]))
  ))
}

linear_influence <- function() {
  cooks <- cooks.distance(lin)
  lev <- hatvalues(lin)
  sres <- rstandard(lin) # internally studentized
  X <- as.matrix(df[, c("x1", "x2")])
  maha <- sqrt(mahalanobis(X, colMeans(X), cov(X)))
  r <- residuals(lin)
  dw <- sum(diff(r)^2) / sum(r^2)
  rows <- list()
  for (i in seq_len(n)) {
    rows[[i]] <- list(mahalanobis = num(maha[i]), cooks = num(cooks[i]),
                      leverage = num(lev[i]), std_resid = num(sres[i]))
  }
  list(error = "", rows = rows, dw = num(dw))
}

# ---- Moderation: y ~ x1 * x2 (StatPrism forms the product column explicitly) ----
moderation_coef <- function() {
  d <- df
  d$inter <- d$x1 * d$x2
  m <- lm(y ~ x1 + x2 + inter, data = d)
  co <- summary(m)$coefficients
  sd_y <- sd(d$y)
  # StatPrism names: const, x1, x2, "x1 * x2" (with &nbsp;); row order is matched positionally.
  cols <- list(c("(Intercept)", NA), c("x1", "x1"), c("x2", "x2"), c("inter", "inter"))
  rows <- list()
  for (cc in cols) {
    nm <- cc[[1]]
    sdcol <- cc[[2]]
    beta <- if (is.na(sdcol)) NA else num(co[nm, "Estimate"] * sd(d[[sdcol]]) / sd_y)
    rows[[length(rows) + 1]] <- list(
      b = num(co[nm, "Estimate"]), se = num(co[nm, "Std. Error"]), beta = beta,
      t = num(co[nm, "t value"]), p = num(co[nm, "Pr(>|t|)"])
    )
  }
  list(error = "", rows = rows)
}

# ---- Mediation: med ~ x1 ; y ~ x1 + med ----
mediation_paths <- function() {
  med_m <- lm(med ~ x1, data = df)
  main_m <- lm(y ~ x1 + med, data = df)
  mc <- summary(med_m)$coefficients
  yc <- summary(main_m)$coefficients
  a <- mc["x1", "Estimate"]
  b_path <- yc["med", "Estimate"]
  path_row <- function(co, nm, from, to) {
    list(from = from, to = to, b = num(co[nm, "Estimate"]), se = num(co[nm, "Std. Error"]),
         t = num(co[nm, "t value"]), p = num(co[nm, "Pr(>|t|)"]))
  }
  rows <- list(
    path_row(mc, "x1", "x1", "med"),
    path_row(yc, "x1", "x1", "y"),
    path_row(yc, "med", "med", "y")
  )
  list(error = "", rows = rows, indirect = list(list(predictor = "x1", value = num(a * b_path))))
}

# ---- Logistic (binary): bin ~ x1 + x2 (positive = "yes") ----
logit <- glm(factor(bin) ~ x1 + x2, family = binomial, data = df)
logit0 <- glm(factor(bin) ~ 1, family = binomial, data = df)

logistic_fit <- function() {
  llf <- as.numeric(logLik(logit))
  lln <- as.numeric(logLik(logit0))
  llr <- logit$null.deviance - logit$deviance
  dfm <- length(coef(logit)) - 1
  list(
    error = "", n = num(n), pseudo_r2 = num(1 - llf / lln), llr_chi2 = num(llr),
    df_model = num(dfm), llr_p = num(pchisq(llr, dfm, lower.tail = FALSE))
  )
}

glm_coef_rows <- function(g) {
  co <- summary(g)$coefficients
  rows <- list()
  for (nm in rownames(co)) {
    rows[[length(rows) + 1]] <- list(
      b = num(co[nm, "Estimate"]), se = num(co[nm, "Std. Error"]),
      odds_ratio = num(exp(co[nm, "Estimate"])), z = num(co[nm, "z value"]), p = num(co[nm, "Pr(>|z|)"])
    )
  }
  rows
}

logistic_coef <- function() list(error = "", rows = glm_coef_rows(logit))

logistic_moderation_coef <- function() {
  # StatPrism adds the moderator and its product with each predictor: bin ~ x1 + x2 + x1:x2.
  g <- glm(factor(bin) ~ x1 + x2 + x1:x2, family = binomial, data = df)
  list(error = "", rows = glm_coef_rows(g))
}

# ---- Multinomial: cat ~ x1 + x2 (reference = "A") ----
mn <- nnet::multinom(factor(cat) ~ x1 + x2, data = df, trace = FALSE)
mn0 <- nnet::multinom(factor(cat) ~ 1, data = df, trace = FALSE)

multinomial_fit <- function() {
  llf <- as.numeric(logLik(mn))
  lln <- as.numeric(logLik(mn0))
  llr <- deviance(mn0) - deviance(mn)
  n_lv <- length(levels(factor(df$cat)))
  dfm <- (n_lv - 1) * 2 # 2 predictors per non-reference equation
  list(
    error = "", n = num(n), pseudo_r2 = num(1 - llf / lln), llr_chi2 = num(llr),
    df_model = num(dfm), llr_p = num(pchisq(llr, dfm, lower.tail = FALSE))
  )
}

multinomial_coef <- function() {
  sm <- summary(mn)
  co <- sm$coefficients      # rows = non-ref categories, cols = terms
  se <- sm$standard.errors
  cats <- rownames(co)
  terms <- colnames(co)
  blocks <- list()
  for (cat in cats) {
    rows <- list()
    for (tm in terms) {
      z <- co[cat, tm] / se[cat, tm]
      rows[[length(rows) + 1]] <- list(
        b = num(co[cat, tm]), se = num(se[cat, tm]), odds_ratio = num(exp(co[cat, tm])),
        z = num(z), p = num(2 * pnorm(-abs(z)))
      )
    }
    blocks[[length(blocks) + 1]] <- list(category = cat, rows = rows)
  }
  list(error = "", blocks = blocks)
}

benchmarks <- list(
  tolerance = 1e-6,
  generated_by = "tests/benchmarks/regression/r/generate_regression_benchmarks.R",
  studies = list(
    linear_fit = linear_fit(),
    linear_coef = linear_coef(),
    linear_vif = linear_vif(),
    linear_influence = linear_influence(),
    moderation_coef = moderation_coef(),
    mediation_paths = mediation_paths(),
    logistic_fit = logistic_fit(),
    logistic_coef = logistic_coef(),
    logistic_moderation_coef = logistic_moderation_coef(),
    multinomial_fit = multinomial_fit(),
    multinomial_coef = multinomial_coef()
  )
)

dir.create(dirname(output_path), recursive = TRUE, showWarnings = FALSE)
jsonlite::write_json(benchmarks, output_path, auto_unbox = TRUE, pretty = TRUE, null = "null", na = "null", digits = NA)
cat("Wrote", output_path, "\n")
