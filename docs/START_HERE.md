# Work through the project

You already have the biological question. The goal now is to understand and improve
an executable analysis, not collect impressive-sounding model names.

## Session 1 — Trust the rows (30–45 minutes)

Open `data/processed/primary_tumor_features.csv` and `docs/ML_AUDIT.md`.
Each row must refer to one primary-tumor sample. Explain what `sample_id`,
`patient_id`, `MCM5`, and `mir885_activity_proxy` actually mean.

**Try:** Run the guided notebook's first data cells. Inspect one specific TCGA ID
in both original files. Explain why independently sorting one column changes the
scientific question. Explain why the proxy's sign was reversed.

**Deliverable:** three sentences describing the repair and the remaining proxy limitation.

## Session 2 — Understand the baseline (45–60 minutes)

Read `src/modeling.py` and the notebook's two-marker example.
StandardScaler centers each feature and divides by its standard deviation;
K-means groups observations to minimize within-cluster squared distances.

**Try:** Change k from 2 to 3 and seed from 52 to 7. Compare size and profiles,
not just colors. Explain why 1,000 clusters for 1,000 points is uninformative.

**Deliverable:** one figure and a paragraph explaining what a cluster means here.

## Session 3 — Challenge the apparent discovery (45–60 minutes)

Read `results/RESULTS.md` and all three metrics CSVs. Compare silhouette with the
Gaussian reference and seed/subsample adjusted Rand indices. Look at GMM BIC,
including its one-component candidate. Do not equate mixture components with disease subtypes.

**Try:** Compare two markers with pathways only. Explain how a stable split can
exist in a continuous distribution. PCA/t-SNE separation alone is not validation.

**Deliverable:** an evidence-based answer to “Have I discovered subtypes?”

## Session 4 — Remove a circular dependency (next research milestone)

The miRNA target signature contains MCM5. Use the original-study repository's
GSVA script to recompute it without MCM5, record package versions, then repeat the
comparison. Do not simply subtract MCM5 expression from a GSVA score.

**Deliverable:** before/after correlation and cluster stability with a stated hypothesis.

## Session 5 — Add biological meaning

Obtain a source-tracked TCGA clinical/sample annotation table. Join by IDs and
quantify LUAD/LUSC, stage, and batch relationships. Keep these labels out of the
unsupervised feature matrix when using them as external checks.
Then identify a compatible independent cohort before claiming generalization.

**Deliverable:** a contingency table and an honest interpretation. Survival modeling
becomes a separate milestone only once valid time/event outcomes are available.

## A sustainable weekly rhythm

Monday: choose one question. Tuesday: understand the method. Wednesday: inspect
inputs. Thursday: specify the experiment. Friday: commit a result and limitation.
Weekend: investigate one failure or read the relevant method paper.

## Your first reply to work through together

After reading the audit, explain in your own words: **what was wrong with the old
ML table, and why doesn't recovering r≈−0.281 prove the proposed regulation?**
We can then walk line by line through `fit_kmeans` and your first controlled change.
