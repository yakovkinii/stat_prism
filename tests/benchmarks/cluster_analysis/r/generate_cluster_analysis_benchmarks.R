args <- commandArgs(trailingOnly = TRUE)
output_path <- if (length(args) >= 1) {
  args[[1]]
} else {
  file.path("tests", "benchmarks", "cluster_analysis", "benchmarks", "cluster_analysis_r_benchmarks.json")
}

for (pkg in c("jsonlite", "cluster")) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    stop(sprintf("Package '%s' is required. Install with install.packages('%s').", pkg, pkg), call. = FALSE)
  }
}

num <- function(v) as.numeric(v)

data_path <- file.path(dirname(dirname(output_path)), "data", "cluster_data.csv")
df <- read.csv(data_path, stringsAsFactors = FALSE)
X <- as.matrix(df[, c("x1", "x2")])

d <- dist(X)

# scipy linkage method -> R hclust method (scipy "ward" == R "ward.D2"; the rest share names).
hclust_method <- list(Ward = "ward.D2", Complete = "complete", Average = "average", Single = "single")

build_study <- function(method_name) {
  h <- hclust(d, method = hclust_method[[method_name]])
  labels <- cutree(h, k = 3)
  sil <- cluster::silhouette(labels, d)
  clusters <- list()
  for (cl in sort(unique(labels))) {
    idx <- which(labels == cl)
    centroid <- colMeans(X[idx, , drop = FALSE])
    clusters[[length(clusters) + 1]] <- list(size = num(length(idx)), centroid = num(centroid))
  }
  # Sort clusters canonically by centroid (x1 then x2) so cluster numbering does not matter.
  ord <- order(
    vapply(clusters, function(z) z$centroid[1], numeric(1)),
    vapply(clusters, function(z) z$centroid[2], numeric(1))
  )
  list(
    error = "", silhouette = num(mean(sil[, "sil_width"])),
    heights = num(sort(h$height)), clusters = clusters[ord]
  )
}

benchmarks <- list(
  tolerance = 1e-6,
  generated_by = "tests/benchmarks/cluster_analysis/r/generate_cluster_analysis_benchmarks.R",
  studies = list(
    hierarchical_ward = build_study("Ward"),
    hierarchical_complete = build_study("Complete"),
    hierarchical_average = build_study("Average"),
    hierarchical_single = build_study("Single")
  )
)

dir.create(dirname(output_path), recursive = TRUE, showWarnings = FALSE)
jsonlite::write_json(benchmarks, output_path, auto_unbox = TRUE, pretty = TRUE, null = "null", na = "null", digits = NA)
cat("Wrote", output_path, "\n")
