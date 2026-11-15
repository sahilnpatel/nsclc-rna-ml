# Exploratory model card

**Intended use:** research learning and hypothesis generation on archived TCGA-derived
expression scores. **Not intended for:** diagnosis, prognosis, treatment selection,
patient risk scoring, or identifying clinically validated subtypes.

Inputs: two-marker (MCM5 and negated miRNA target score), 11 saved pathways, or all 13.
Cohort: 1,017 unique primary-tumor patients after sample-ID joins. No clinical subtype
labels supplied. Genes and pathway choices came from prior same-cohort research.

Preprocessing: StandardScaler per feature, no imputation; nonfinite input fails.
Model: K-means++, 20 starts, seed 52; k=2–8. Selection: maximum in-cohort
silhouette (up to 600 fixed-seed sampled observations), tie to smaller k.
Comparison: full-covariance GMM, 1–8 components, five initializations, BIC/AIC.
Robustness: eight seed repeats and eight 80%-sample fits; adjusted Rand index
against full-cohort reference predictions. Null diagnostic: eight simulated
single correlated Gaussian datasets with matching dimensions/covariance.

Export: JSON stores exact feature order, scaler mean/scale, and standardized centers.
Assignment is nearest squared-Euclidean center after scaling. These assignments
are arbitrary labels, not probabilities, patient classes, or a clinical prediction.

Key limitations: proxy circularity (MCM5 in signature), overlapping gene sets,
unknown batch/subtype composition, original score normalization across the complete
cohort, no independent cohort or survival labels. Training and selection use the
same exploratory cohort; no claimed out-of-sample accuracy.

See summary.json for package versions, seeds, source hashes, and run settings.
