# Validation

Local test suite: 10 tests passed across the two repositories (3 original-study,
7 ML). The source audit and descriptive reanalysis completed. All three ML feature
sets completed with eight stability repeats and optional t-SNE. Independent
nearest-center, inertia, and PCA projection checks passed on the real data.

The local Accelerate/NumPy runtime emits matrix-operation warnings despite finite,
consistent results. These are recorded as a reproducibility concern, not suppressed
or dismissed. Linux CI is provided to test a clean, separate environment and save
fresh outputs as an Actions artifact. Inspect its actual status before claiming a
cross-platform reproduction. The R/GSVA rerun has not been executed.
