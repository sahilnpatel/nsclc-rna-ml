"""Run the complete exploratory benchmark on audited, ID-matched source data."""
import argparse
import hashlib
import importlib.metadata
import json
import sys
from pathlib import Path
import numpy as np
from scipy.stats import pearsonr
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from scipy.spatial.distance import cdist

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from data_io import aligned_rows, write_csv
from modeling import benchmark
from plots import scatter, lines


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--repeats',type=int,default=8)
    parser.add_argument('--seed',type=int,default=52)
    parser.add_argument('--tsne',action='store_true',help='Optional visualization only; never used for fitting clusters')
    args=parser.parse_args()
    if args.repeats < 2: raise ValueError('Use at least two stability repeats')
    all_rows=aligned_rows(ROOT/'data/source')
    rows=[r for r in all_rows if r['sample_type']=='01']
    if len({r['patient_id'] for r in rows})!=len(rows):raise ValueError('Duplicate patients')
    write_csv(ROOT/'data/processed/primary_tumor_features.csv',rows)
    out=ROOT/'results'; out.mkdir(exist_ok=True)
    pathways=[k for k in rows[0] if k.startswith(('GOBP_','REACTOME_'))]
    feature_sets={'two_marker':['MCM5','mir885_activity_proxy'], 'pathways':pathways,
                  'combined':['MCM5','mir885_activity_proxy',*pathways]}
    summary={'seed':args.seed,'repeats':args.repeats,'n_samples':len(rows),'cohort':'primary tumors only',
             'versions':{p:importlib.metadata.version(p) for p in ['numpy','scipy','scikit-learn']},
             'source_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'data/source').glob('*.tsv'))},
             'experiments':{},'limitations':['Exploratory same-cohort selection; no external validation.',
             'The miRNA proxy signature contains MCM5.', 'Pathway features overlap biologically and are not independent.',
             'No direct circRNA/miRNA assay, survival, stage, batch, or LUAD/LUSC annotations.',
             'A best-k candidate does not establish discrete biological subtypes.']}
    for name,features in feature_sets.items():
        X=np.array([[r[f] for f in features] for r in rows])
        metrics, model, gmm=benchmark(X,repeats=args.repeats,seed=args.seed)
        k=int(model[-1].n_clusters); labels=model.predict(X); Z=model[0].transform(X)
        # Independent checks avoid BLAS matrix products and detect invalid local numerics.
        distances=cdist(Z,model[-1].cluster_centers_,metric='sqeuclidean')
        if not np.isfinite(distances).all() or not np.array_equal(distances.argmin(1),labels):
            raise ValueError('Independent nearest-center check failed')
        if not np.isclose(distances[np.arange(len(Z)),labels].sum(),model[-1].inertia_,rtol=1e-8):
            raise ValueError('Independent inertia check failed')
        write_csv(out/f'{name}_metrics.csv',metrics); write_csv(out/f'{name}_gmm.csv',gmm)
        write_csv(out/f'{name}_assignments.csv',[{'sample_id':r['sample_id'],'cluster':int(l)} for r,l in zip(rows,labels)])
        profiles=[]
        for group in range(k):
            mask=labels==group
            profiles.append({'cluster':group,'n':int(mask.sum()),**{f:float(X[mask,j].mean()) for j,f in enumerate(features)}})
        write_csv(out/f'{name}_profiles.csv',profiles)
        pca=PCA(n_components=2).fit(Z); view=pca.transform(Z)
        if not np.isfinite(view).all() or not np.allclose(view,np.einsum('ij,kj->ik',Z-pca.mean_,pca.components_,optimize=False)):
            raise ValueError('Independent PCA projection check failed')
        scatter(out/f'{name}_pca.svg',view[:,0],view[:,1],labels,f'{name}: exploratory K-means (k={k})',
                f'PC1 ({pca.explained_variance_ratio_[0]:.1%} variance)',f'PC2 ({pca.explained_variance_ratio_[1]:.1%} variance)')
        lines(out/f'{name}_selection.svg',[m['k'] for m in metrics],
              {'Observed silhouette':[m['silhouette'] for m in metrics],
               'Single-Gaussian reference':[m['null_silhouette_mean'] for m in metrics]},
              f'{name}: cluster separation against a reference','Silhouette (subsampled)')
        if args.tsne:
            view_tsne=TSNE(n_components=2,perplexity=30,random_state=args.seed,init='pca',learning_rate='auto').fit_transform(Z)
            scatter(out/f'{name}_tsne.svg',view_tsne[:,0],view_tsne[:,1],labels,f'{name}: t-SNE display only','t-SNE 1','t-SNE 2')
        chosen=next(m for m in metrics if m['k']==k)
        summary['experiments'][name]={'features':features,'candidate_k':k,'candidate_metrics':chosen,
                                     'gmm_bic_candidate':min(gmm,key=lambda r:r['bic'])['components'],
                                     'pca_variance_explained':pca.explained_variance_ratio_.tolist()}
        # Portable inference metadata; avoids untrusted pickle execution and includes scaler.
        (out/f'{name}_model.json').write_text(json.dumps({'feature_order':features,'mean':model[0].mean_.tolist(),
              'scale':model[0].scale_.tolist(),'centers':model[-1].cluster_centers_.tolist(),
              'purpose':'Exploratory nearest-center assignment, not a clinical classifier'},indent=2))
        print(name, 'candidate k=',k,'silhouette=',round(chosen['silhouette'],3),flush=True)
    proxy=[r['mir885_activity_proxy'] for r in rows]; mcm=[r['MCM5'] for r in rows]
    summary['primary_tumor_correlation']=float(pearsonr(proxy,mcm).statistic)
    scatter(out/'aligned_markers.svg',proxy,mcm,[0]*len(rows),'Sample-aligned primary tumors','Inferred miR-885-3p activity (proxy)','MCM5 expression (saved scale)')
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    table='\n'.join(f"| {n} | {v['candidate_k']} | {v['candidate_metrics']['silhouette']:.3f} | {v['candidate_metrics']['null_silhouette_mean']:.3f} | {v['candidate_metrics']['subsample_ari_mean']:.3f} |" for n,v in summary['experiments'].items())
    (out/'RESULTS.md').write_text(f'''# Exploratory ML results

Run on {len(rows)} sample-ID-aligned primary tumors, seed {args.seed}, {args.repeats} stability repeats.

| Feature set | Candidate k | Silhouette | Gaussian reference | Subsample stability (ARI) |
|---|---:|---:|---:|---:|
{table}

Candidate k maximizes silhouette over 2–8 on the same cohort. It is a descriptive
choice, not a validated biological subtype count. Compare with the single-Gaussian
reference before interpreting a partition: K-means also partitions continuous clouds.
The reference is a diagnostic comparison, not a calibrated hypothesis test.

![Aligned markers](aligned_markers.svg)
![Two-marker selection](two_marker_selection.svg)
![Pathway projection](pathways_pca.svg)

## What is established

The workflow is executable, uses keyed joins, excludes normal/recurrent tissue by
default, and compares feature sets with fixed settings. The all-sample original
correlation is reproducible from saved exports; the old ML export was mispaired.

## What remains open

Do these partitions persist without MCM5 in the proxy signature? Do they primarily
reflect LUAD versus LUSC, batch, or proliferation? Are they reproducible externally?
No novel subtype, causal regulation, diagnostic performance, or survival prediction
is established here. Saved pathway scores were originally estimated across the
full cohort, including normal samples; this is exploratory reuse, not held-out testing.

PCA of the two-marker feature set is only a rotation of two inputs, not meaningful
dimension reduction. Optional t-SNE is a display, never evidence of distinct groups.
''')


if __name__=='__main__':main()
