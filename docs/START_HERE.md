# Working through the analysis

Start with the data repair, then fit a small model before running the full set of
experiments. The notebook follows the same order.

## 1. Check sample matching

Read [the data audit](ML_AUDIT.md) and open
`data/processed/primary_tumor_features.csv`. Pick one TCGA sample ID and find it in
both original source files. Check that its MCM5 value and target score match the
processed row.

The old table sorted the MCM5 column independently, so values from different
samples ended up on the same row. Matching by sample ID fixes this. The other
important detail is that `mir885_activity_proxy` is a negated target-gene score,
not a measurement of miRNA expression.

Before moving on, explain why recovering the paper's correlation does not prove
the proposed regulatory mechanism.

## 2. Fit the two-marker baseline

Run the notebook's K-means example and read `fit_kmeans` in `src/modeling.py`.
StandardScaler centers each feature and divides by its standard deviation.
K-means then groups samples to minimize squared distances to their cluster centers.

Change k from 2 to 3, then change the seed from 52 to 7. Compare cluster sizes and
average feature values. Save one figure and note what changed. The original
notebooks used 1,000 clusters for 1,000 observations, which cannot provide useful
groups of samples.

## 3. Check what the clusters actually tell us

Read [the results](../results/RESULTS.md) alongside the metrics CSVs. Compare the
silhouette scores with the Gaussian reference and check seed/subsample stability.
Also look at GMM BIC, including the one-component model.

A stable split can still divide a continuous distribution. Compare the two-marker
and pathway-only results: is there evidence for distinct groups, or mostly a
consistent way of splitting the data? A separated PCA or t-SNE plot is not enough
to answer that question.

## 4. Recompute the signature without MCM5

MCM5 is one of the 74 genes used to construct the target score. That makes its
correlation with the score harder to interpret.

Use `scripts/recompute_gsva.R` in the original-study repository to calculate the
signature without MCM5, then repeat the analysis. Record the package versions,
before/after correlations, and cluster stability. A GSVA score needs to be
recomputed; subtracting MCM5 expression from the existing score will not work.

Write down the expected effect before running this experiment.

## 5. Add clinical annotations

Obtain a documented TCGA sample/clinical table and join it by sample or patient ID.
Check whether the clusters correspond to LUAD versus LUSC, stage, or batch. Keep
those annotations out of the clustering features if they are being used to check
the results.

An independent cohort would provide a stronger next test. Survival modeling needs
valid time and event data, which are not included yet.
