import sys
from pathlib import Path
import numpy as np
import pytest
from sklearn.datasets import make_blobs
from sklearn.metrics import adjusted_rand_score
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from data_io import aligned_rows, read_matrix
from modeling import fit_kmeans, validate


def test_known_separated_clusters():
    X,y=make_blobs(n_samples=90,centers=[(-8,-8),(0,8),(8,-8)],cluster_std=.3,random_state=2)
    model=fit_kmeans(X,3)
    assert adjusted_rand_score(y,model.predict(X))>.99


def test_singletons_rejected():
    with pytest.raises(ValueError):fit_kmeans(np.arange(200).reshape(100,2),100)


def test_nonfinite_and_constant_rejected():
    with pytest.raises(ValueError):validate(np.ones((20,2)))
    X=np.arange(40,dtype=float).reshape(20,2);X[1,0]=np.nan
    with pytest.raises(ValueError):validate(X)


def test_join_is_order_independent(tmp_path):
    from shutil import copyfile
    import csv
    for f in (ROOT/'data/source').glob('*.tsv'):copyfile(f,tmp_path/f.name)
    original=aligned_rows(tmp_path)
    path=tmp_path/'mcm5.tsv'
    rows=list(csv.reader(path.open(),delimiter='\t'))
    rows[0]=rows[0][::-1];rows[1]=[rows[1][0],*rows[1][1:][::-1]]
    with path.open('w') as s:csv.writer(s,delimiter='\t').writerows(rows)
    assert aligned_rows(tmp_path)==original


def test_duplicate_ids_fail(tmp_path):
    p=tmp_path/'bad.tsv';p.write_text('TCGA-AA-0001-01\tTCGA-AA-0001-01\nx\t1\t2\n')
    with pytest.raises(ValueError,match='Duplicate'):read_matrix(p)


def test_recovered_cohort():
    rows=aligned_rows(ROOT/'data/source')
    assert len(rows)==1129
    tumor=[r for r in rows if r['sample_type']=='01']
    assert len(tumor)==1017
    assert len({r['patient_id'] for r in tumor})==1017
    assert 'MCM5' in rows[0] and len([k for k in rows[0] if k.startswith(('GOBP_','REACTOME_'))])==11
    r=np.corrcoef([r['MCM5'] for r in rows],[r['mir885_activity_proxy'] for r in rows])[0,1]
    assert abs(r-(-.2809100973771341))<1e-10


def test_portable_model_matches_pipeline():
    X,_=make_blobs(n_samples=50,centers=2,n_features=2,random_state=8)
    model=fit_kmeans(X,2)
    z=(X-model[0].mean_)/model[0].scale_
    pred=((z[:,None,:]-model[-1].cluster_centers_[None,:,:])**2).sum(2).argmin(1)
    np.testing.assert_array_equal(pred,model.predict(X))
