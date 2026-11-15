# NSCLC RNA machine learning

After finishing my high-school circRNA study, I began exploring machine learning
with a collaborator at Vanderbilt. That work was never completed. This repository
picks it back up, starting with the data and the original clustering notebooks.

The question is whether MCM5 expression, an inferred miR-885-3p activity score,
and pathway scores reveal useful patterns across primary NSCLC tumors. The
current analysis compares K-means and Gaussian mixtures across three feature
sets, then checks how much the results change across seeds and subsamples.

The pipeline runs and the results are saved here. Whether these patterns have
biological significance is still an open question.

## What changed

The old ML spreadsheet paired original-order miRNA proxy scores with independently
sorted MCM5 values. Both historical notebooks also requested 1,000 clusters for
1,000 observations. Those runs are archived, not used as valid results.
The new workflow joins by TCGA ID and analyzes **1,017 primary tumors**.

Read [the original-study audit](https://github.com/sahilnpatel/circrna-mirna-mrna)
and [the ML audit](docs/ML_AUDIT.md) before interpreting the figures.

## Run the project

Follow [environment setup](docs/ENVIRONMENT.md), then from this repository root:

```bash
python scripts/run_analysis.py
python -m pytest tests -q
# Optional visualization; clustering is never fitted in t-SNE coordinates:
python scripts/run_analysis.py --tsne
```

No downloaded raw matrix is needed for this saved-output analysis. The saved
inputs are in `data/source`. New score computation is a separate
step in the original-study repository.

## Results

Read [the results](results/RESULTS.md) and [machine-readable summary](results/summary.json).
The tested settings favor k=2 for all three feature sets, but silhouettes are close
to those of a single correlated Gaussian. Stable partitions can divide a continuous
cloud: stability alone does not show that distinct biological populations exist.

![Sample-aligned markers](results/aligned_markers.svg)
![Cluster-selection diagnostic](results/two_marker_selection.svg)

## Exploring the analysis

The [walkthrough](docs/START_HERE.md) covers sample matching, fitting a baseline,
and interpreting the results. The [notebook](notebooks/01_work_through_the_project.ipynb)
provides a small example to run and modify before working with the full pipeline.

## Files

| Folder | Purpose |
|---|---|
| `archive` | Original notebooks, outputs cleared and local paths redacted |
| `data/source` | Original keyed MCM5, target-score, and pathway exports |
| `data/processed` | Primary tumor features rebuilt by keyed joins |
| `src` | Data checks, modeling, and SVG figure utilities |
| `scripts` | Reproducible experiment entry point |
| `results` | Metrics, assignments, profiles, figures, portable models |
| `notebooks` | Guided executable learning walkthrough |
| `tests` | Alignment, invalid-input, clustering, and model-export checks |
| `docs` | Audit, experimental design, model card, and next tasks |

## Limitations

- No direct circRNA or miRNA assay: the miRNA variable is a target-score proxy.
- MCM5 is part of that signature. Leave-MCM5-out recomputation is a priority.
- No clinical subtype, batch, stage, outcome, or independent validation dataset.
- All metrics are exploratory, in-cohort diagnostics; not predictive accuracy.
- Original pathway scores were estimated across the full historical cohort.

[Model card](docs/MODEL_CARD.md) · [references](docs/REFERENCES.md) ·
[credit and rights](docs/RIGHTS_AND_CREDIT.md)
