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

# scipy linkage(method="ward") on raw observations matches R hclust(dist, method="ward.D2").
d <- dist(X)
h <- hclust(d, method = "ward.D2")
labels <- cutree(h, k = 3)

sil <- cluster::silhouette(labels, d)
silhouette <- mean(sil[, "sil_width"])

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
clusters <- clusters[ord]

benchmarks <- list(
  tolerance = 1e-6,
  generated_by = "tests/benchmarks/cluster_analysis/r/generate_cluster_analysis_benchmarks.R",
  studies = list(
    hierarchical_ward = list(
      error = "",
      silhouette = num(silhouette),
      heights = num(sort(h$height)),
      clusters = clusters
    )
  )
)

dir.create(dirname(output_path), recursive = TRUE, showWarnings = FALSE)
jsonlite::write_json(benchmarks, output_path, auto_unbox = TRUE, pretty = TRUE, null = "null", na = "null", digits = NA)
cat("Wrote", output_path, "\n")
