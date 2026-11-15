# Audit of the unfinished ML work

## Recovered material

Two notebooks (`RNA Machine Learning.ipynb`, `ML II .ipynb`), a labeled CSV,
a pickle, a two-column source spreadsheet, and the two supplied explanatory notes.
The notes discuss t-SNE and smaller cluster counts, but the recovered notebook
code contains K-means/PCA and a 2,7,12,...,47 cluster-count sweep. It does not
establish that all suggested analyses were completed. The new t-SNE code is a
new implementation, not an assertion about historical work.

## Verified problems

1. Both notebooks specify `n_clusters=1000`; their printed output has 1,000 rows.
2. Every historical ML miRNA value matches the first 1,000 original-order negative
   target scores (within rounding tolerance). Every MCM5 value matches the first
   1,000 independently sorted MCM5 values. This destroys sample correspondence.
3. The 1,000-row sheet drops 129 observations without a documented inclusion rule.
4. Neither feature is circRNA. The miRNA column is inferred activity, not a direct assay.
5. The source mixes primary tumor, recurrent tumor, and normal tissue.
6. The target signature includes MCM5, potentially contributing mechanically to correlation.
7. The notebooks retain `data` and a cleaned `df`, then append labels to `data`.
   This is fragile if cleaning changes row count or order.
8. No saved scaler accompanies the located old pickle. It is excluded, never loaded.
9. PCA of two inputs into two components changes coordinates but does not reduce dimension.
10. No survival/clinical endpoint table or external validation was recovered.

## Rebuild decisions

Strict keyed joins; duplicate/nonfinite checks; one primary tumor per patient;
fixed preprocessing and seeds; explicit `n_init=20`; k=2–8; repeated seeds;
80% subsampling with scaler refit; silhouette and size diagnostics; continuous
Gaussian reference; GMM BIC including one component; all data and limitations saved.

Subsampling stability is evaluated by predicting all original observations after
fitting on the subsample. It is an in-cohort reproducibility measure, not a held-out
performance estimate. Candidate k is selected descriptively on the same data.
