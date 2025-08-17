from typing import Tuple

import numpy as np
import pandas as pd
from factor_analyzer import FactorAnalyzer
from scipy.stats import chi2
from numpy.linalg import inv, svd, eigh

from src.common.decorators import log_function
from src.data.data import Data
from src.modules.common.result.html_result import Cell, HTMLTableV2, Row
from src.modules.exploratory_factor_analysis.result import (
    ExtractionMethod,
    FactorAnalysisResult,
    RotationType,
)


def _standardize(df: pd.DataFrame) -> pd.DataFrame:
    return (df - df.mean()) / df.std(ddof=0)


def _correlation_matrix(X: np.ndarray) -> np.ndarray:
    return np.corrcoef(X, rowvar=False)


def _kmo_bartlett(R: np.ndarray, n_samples: int) -> Tuple[float, np.ndarray, float, float, int]:
    # KMO
    invR = inv(R)
    partial = -invR / np.sqrt(np.outer(np.diag(invR), np.diag(invR)))
    np.fill_diagonal(partial, 0.0)
    r2 = R ** 2
    np.fill_diagonal(r2, 0.0)
    p2 = partial ** 2
    kmo_num = np.sum(r2)
    kmo_den = kmo_num + np.sum(p2)
    kmo_overall = kmo_num / kmo_den if kmo_den != 0 else np.nan
    msa = 1.0 - (np.sum(p2, axis=0) / (np.sum(p2, axis=0) + np.sum(r2, axis=0)))

    # Bartlett's test
    p = R.shape[0]
    detR = np.linalg.det(R)
    if detR <= 0:
        # numerical guard
        detR = max(detR, 1e-16)
    chi2_stat = -(n_samples - 1 - (2 * p + 5) / 6) * np.log(detR)
    dof = p * (p - 1) // 2
    p_value = 1 - chi2.cdf(chi2_stat, dof)
    return kmo_overall, msa, chi2_stat, p_value, dof


def _orthomax_rotation(loadings: np.ndarray, gamma: float = 1.0, normalize: bool = True, tol=1e-7, max_iter=500):
    # Varimax: gamma=1, Quartimax: gamma=0, Equamax: gamma=p/2
    L = loadings.copy()
    n_rows, n_cols = L.shape
    if normalize:
        # Kaiser normalization
        h2 = np.sum(L ** 2, axis=1)
        s = np.sqrt(h2)
        s[s == 0] = 1.0
        L = (L.T / s).T
    else:
        s = np.ones(n_rows)
    Rmat = np.eye(n_cols)
    for _ in range(max_iter):
        Lambda = L @ Rmat
        u, _, vT = svd(Lambda.T @ (Lambda ** 3 - (gamma / n_rows) * Lambda @ np.diag(np.sum(Lambda ** 2, axis=0))))
        Rnew = u @ vT
        if np.max(np.abs(Rmat - Rnew)) < tol:
            Rmat = Rnew
            break
        Rmat = Rnew
    Lrot = L @ Rmat
    if normalize:
        Lrot = (Lrot.T * s).T  # de-normalize
    return Lrot, Rmat


def _varimax(loadings, kaiser=True):
    gamma = 1.0
    return _orthomax_rotation(loadings, gamma=gamma, normalize=kaiser)


def _quartimax(loadings, kaiser=True):
    gamma = 0.0
    return _orthomax_rotation(loadings, gamma=gamma, normalize=kaiser)


def _equamax(loadings, kaiser=True):
    # gamma = p/2
    p = loadings.shape[0]
    gamma = p / 2.0
    return _orthomax_rotation(loadings, gamma=gamma, normalize=kaiser)


def _promax(loadings: np.ndarray, power: int = 4, kaiser: bool = True):
    # 1) start with varimax
    L0, _ = _varimax(loadings, kaiser)
    # 2) build target
    T = np.sign(L0) * (np.abs(L0) ** power)
    # 3) least-squares regression to target (oblique)
    B = np.linalg.pinv(L0) @ T  # (m x m)
    # 4) pattern matrix
    P = L0 @ B
    # 5) factor correlation matrix
    Phi = np.linalg.inv(B.T @ B)
    # Ensure symmetry
    Phi = (Phi + Phi.T) / 2.0
    return P, B, Phi


def _oblimin(loadings, gamma=0.0, tol=1e-7, max_iter=500):
    # Direct oblimin rotation (Jennrich & Sampson, 1966)
    # gamma=0: quartimin, gamma=1: covarimin
    L = loadings.copy()
    n_rows, n_cols = L.shape
    T = np.eye(n_cols)
    for _ in range(max_iter):
        Lambda = L @ T
        # Compute the gradient
        phi = Lambda @ Lambda.T
        grad = Lambda * (phi @ Lambda) - gamma * Lambda * (np.sum(Lambda ** 2, axis=1, keepdims=True))
        u, _, vT = svd(Lambda.T @ grad)
        Tnew = u @ vT
        if np.max(np.abs(T - Tnew)) < tol:
            T = Tnew
            break
        T = Tnew
    Lrot = L @ T
    # Estimate factor correlation matrix
    Phi = np.linalg.inv(T.T @ T)
    return Lrot, T, Phi


def _geomin(loadings, epsilon=0.01, tol=1e-7, max_iter=500):
    # Geomin rotation (Yates, 1987; Browne, 2001)
    L = loadings.copy()
    n_rows, n_cols = L.shape
    T = np.eye(n_cols)
    for _ in range(max_iter):
        Lambda = L @ T
        # Geomin criterion: minimize the geometric mean of squared loadings per variable
        geo_mean = np.exp(np.mean(np.log(Lambda ** 2 + epsilon), axis=1, keepdims=True))
        grad = Lambda / (Lambda ** 2 + epsilon) * geo_mean
        u, _, vT = svd(Lambda.T @ grad)
        Tnew = u @ vT
        if np.max(np.abs(T - Tnew)) < tol:
            T = Tnew
            break
        T = Tnew
    Lrot = L @ T
    # Estimate factor correlation matrix
    Phi = np.linalg.inv(T.T @ T)
    return Lrot, T, Phi


def _principal_axis_from_corr(R: np.ndarray, n_factors: int) -> Tuple[np.ndarray, np.ndarray]:
    # PCA-based approximation: loadings = eigenvectors * sqrt(eigenvalues)
    evals, evecs = eigh(R)
    idx = np.argsort(evals)[::-1]
    evals = evals[idx]
    evecs = evecs[:, idx]
    m = n_factors
    L = evecs[:, :m] * np.sqrt(np.clip(evals[:m], 0, None))
    uniq = 1.0 - np.sum(L ** 2, axis=1)
    uniq = np.clip(uniq, 1e-6, None)
    return L, uniq


@log_function
def recalculate_factor_analysis_study(data: Data, result: FactorAnalysisResult) -> FactorAnalysisResult:
    cfg = result.config
    df = data.get_dataframe(filters=cfg.filters, columns=cfg.columns, map_ordinal=False)

    if df is None or df.shape[1] < 2:
        result.set_placeholder("Select at least two variables.")
        return result

    # Keep only numeric columns
    df = df.select_dtypes(include=[np.number]).astype(float)
    df = df.dropna(axis=0)  # listwise
    n_rows, n_cols = df.shape
    if n_rows < 5 or n_cols < 2:
        result.set_placeholder("Not enough complete data for EFA.")
        return result

    # Sanity check: n_factors <= n_cols
    m = cfg.n_factors
    if m > n_cols:
        result.set_placeholder(f"Number of factors ({m}) cannot exceed number of variables ({n_cols}).")
        return result

    X = df.values
    n, p = X.shape

    # Diagnostics
    R = np.corrcoef(X, rowvar=False)
    kmo_overall, msa, bart_chi2, bart_p, bart_df = _kmo_bartlett(R, n)

    # Eigenvalues (scree)
    evals, _ = np.linalg.eigh(R)
    evals = np.sort(evals)[::-1]
    explained = evals / np.sum(evals) * 100.0

    # Suggest optimal number of factors (Kaiser criterion: eigenvalue > 1)
    n_optimal = np.sum(evals > 1)
    eig_table = HTMLTableV2(table_caption="Eigenvalues (Correlation Matrix)")
    eig_table.add_single_row_apa(Row([Cell("Component"), Cell("Eigenvalue"), Cell("% of Variance")]))
    for i, (ev, ex) in enumerate(zip(evals, explained), 1):
        eig_table.add_single_row_apa(Row([Cell(f"{i}"), Cell(f"{ev:.3f}"), Cell(f"{ex:.1f}")]))
    if n_optimal > 0:
        eig_table.add_text(f"Suggested number of factors (Kaiser criterion, eigenvalue > 1): <b>{n_optimal}</b>")
    else:
        eig_table.add_text("No eigenvalues > 1. Consider using a scree plot or parallel analysis for factor selection.")

    # Extraction and Rotation using factor_analyzer
    rotation_map = {
        RotationType.VARIMAX: 'varimax',
        RotationType.PROMAX: 'promax',
        RotationType.OBLIMIN: 'oblimin',
        RotationType.OBLIMAX: 'oblimax',
        RotationType.QUARTIMIN: 'quartimin',
        RotationType.QUARTIMAX: 'quartimax',
        RotationType.EQUAMAX: 'equamax',
        RotationType.NONE: None,
    }
    method_map = {
        ExtractionMethod.MINRES: 'minres',
        ExtractionMethod.ML: 'ml',
        ExtractionMethod.PRINCIPAL: 'principal',
    }
    rotation = rotation_map.get(cfg.rotation, None)
    method = method_map[cfg.method]

    if cfg.kaiser_normalization:
        rotation_kwargs = {'normalize': True}
    else:
        rotation_kwargs = {'normalize': False}

    fa = FactorAnalyzer(
        n_factors=m,
        method=method,
        rotation=rotation,
        use_smc=True,
        rotation_kwargs=rotation_kwargs
    )
    fa.fit(X)
    loadings = fa.loadings_
    if rotation in ['promax', 'oblimin', 'geomin_obl']:
        phi = fa.phi_
    else:
        phi = np.eye(m)

    # Communalities / uniquenesses
    if rotation in ['promax', 'oblimin', 'geomin_obl']:
        h2 = np.sum((loadings @ phi) * loadings, axis=1)
    else:
        h2 = np.sum(loadings ** 2, axis=1)
    u2 = np.clip(1.0 - h2, 0.0, None)

    # Tables
    diag_table = HTMLTableV2(table_caption="KMO and Bartlett's Test")
    diag_table.add_single_row_apa(Row([Cell("KMO (overall)"), Cell(f"{kmo_overall:.3f}")]))
    for name, val in zip(df.columns, msa):
        diag_table.add_single_row_apa(Row([Cell(f"MSA: {name}"), Cell(f"{val:.3f}")]))
    diag_table.add_single_row_apa(Row([Cell("Bartlett's χ²"), Cell(f"{bart_chi2:.3f}")]))
    diag_table.add_single_row_apa(Row([Cell("df"), Cell(f"{bart_df}")]))
    diag_table.add_single_row_apa(Row([Cell("p-value"), Cell(f"{bart_p:.5f}")]))

    load_table = HTMLTableV2(table_caption=f"Factor Loadings ({cfg.rotation.value})")
    headers = [Cell("Variable")] + [Cell(f"F{i+1}") for i in range(m)] + [Cell("Communality"), Cell("Uniqueness")]
    load_table.add_single_row_apa(Row(headers))
    for idx, var in enumerate(df.columns):
        row = [Cell(var)]
        for j in range(m):
            row.append(Cell(f"{loadings[idx, j]:.3f}"))
        row.append(Cell(f"{h2[idx]:.3f}"))
        row.append(Cell(f"{u2[idx]:.3f}"))
        load_table.add_single_row_apa(Row(row))

    result.result_elements = [diag_table, eig_table, load_table]

    # 4) Factor correlations (oblique) and Structure matrix
    if rotation in ['promax', 'oblimin', 'geomin_obl']:
        phi_table = HTMLTableV2(table_caption="Factor Correlation Matrix (Phi)")
        phi_table.add_single_row_apa(Row([Cell("")] + [Cell(f"F{i+1}") for i in range(m)]))
        for i in range(m):
            row = [Cell(f"F{i+1}")]
            for j in range(m):
                row.append(Cell(f"{phi[i, j]:.3f}"))
            phi_table.add_single_row_apa(Row(row))
        result.result_elements.append(phi_table)

        S = loadings @ phi
        struct_table = HTMLTableV2(table_caption="Structure Matrix")
        struct_table.add_single_row_apa(Row([Cell("Variable")] + [Cell(f"F{i+1}") for i in range(m)]))
        for idx, var in enumerate(df.columns):
            row = [Cell(var)] + [Cell(f"{S[idx, j]:.3f}") for j in range(m)]
            struct_table.add_single_row_apa(Row(row))
        result.result_elements.append(struct_table)

    # Header with method/rotation info
    result.header = ""
    result.add_header_info(f"Method: <i>{cfg.method.value.upper()}</i>; Rotation: <i>{cfg.rotation.value}</i>; Factors: <i>{m}</i>")
    return result
