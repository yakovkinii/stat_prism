from __future__ import annotations

from pathlib import Path

import pandas as pd

_DIR = Path(__file__).resolve().parent / "data"
DATA_PATH = _DIR / "efa_data.csv"
LIKERT_DATA_PATH = _DIR / "efa_likert_data.csv"


def efa_data() -> pd.DataFrame:
    # 6 items with a clean 2-factor structure (v1-v3 / v4-v6), read identically by Python and R.
    return pd.read_csv(DATA_PATH)


def efa_likert_data() -> pd.DataFrame:
    # Five-category Likert version (for the polychoric path), read identically by Python and R.
    return pd.read_csv(LIKERT_DATA_PATH)


# All three studies come from one EFA run: Pearson correlation, MINRES extraction, NO rotation
# (rotation conventions between factor_analyzer and psych differ and are deferred to a later pass),
# 2 factors. Diagnostics and eigenvalues share the same formulas as psych; loadings are compared after
# a canonical sign/column alignment because the raw sign and factor order are not identified.
CASES = [
    {"study": "diagnostics", "kind": "efa_diagnostics"},
    {"study": "eigenvalues", "kind": "efa_eigenvalues"},
    {"study": "loadings_unrotated", "kind": "efa_loadings"},
    # Extraction methods (unrotated): MINRES (above), ML, Principal Axis.
    {"study": "loadings_ml", "method": "Maximum Likelihood (ML)", "kind": "efa_loadings"},
    {"study": "loadings_principal", "method": "Principal Axis (PAF)", "kind": "efa_loadings"},
    # Orthogonal rotations (MINRES): each yields a loadings table (no factor correlation).
    {"study": "loadings_varimax", "rotation": "varimax", "kind": "efa_loadings"},
    {"study": "loadings_quartimax", "rotation": "quartimax", "kind": "efa_loadings"},
    {"study": "loadings_equamax", "rotation": "equamax", "kind": "efa_loadings"},
    # Oblique rotations (MINRES): loadings + factor correlation (phi) + structure matrix.
    {"study": "loadings_promax", "rotation": "promax (obl)", "kind": "efa_loadings"},
    {"study": "loadings_oblimin", "rotation": "oblimin (obl)", "kind": "efa_loadings"},
    {"study": "loadings_quartimin", "rotation": "quartimin (obl)", "kind": "efa_loadings"},
    {"study": "phi_promax", "rotation": "promax (obl)", "kind": "efa_phi"},
    {"study": "phi_oblimin", "rotation": "oblimin (obl)", "kind": "efa_phi"},
    {"study": "structure_promax", "rotation": "promax (obl)", "kind": "efa_structure"},
    {"study": "structure_oblimin", "rotation": "oblimin (obl)", "kind": "efa_structure"},
    # Polychoric correlation path: diagnostics, eigenvalues and (unrotated) loadings from the
    # polychoric matrix instead of Pearson.
    {
        "study": "diagnostics_poly",
        "correlation_method": "Polychoric",
        "data": efa_likert_data,
        "kind": "efa_diagnostics",
    },
    {
        "study": "eigenvalues_poly",
        "correlation_method": "Polychoric",
        "data": efa_likert_data,
        "kind": "efa_eigenvalues",
    },
    {"study": "loadings_poly", "correlation_method": "Polychoric", "data": efa_likert_data, "kind": "efa_loadings"},
]
