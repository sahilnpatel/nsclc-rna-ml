"""Exploratory models. Cluster labels are not clinical ground truth."""
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.mixture import GaussianMixture
from sklearn.pipeline import make_pipeline


def validate(X):
    X = np.asarray(X, dtype=float)
    if X.ndim != 2 or X.shape[0] < 10 or X.shape[1] < 2:
        raise ValueError('Require at least 10 rows and two features')
    if not np.isfinite(X).all():
        raise ValueError('Missing or nonfinite feature values')
    if np.any(np.std(X, axis=0) == 0):
        raise ValueError('Constant features must be removed explicitly')
    return X


def fit_kmeans(X, k, seed=52):
    X = validate(X)
    if k < 2 or k > min(8, len(X)//5) or k >= len(np.unique(X, axis=0)):
        raise ValueError('Use 2–8 clusters, at least five observations per requested cluster')
    model = make_pipeline(StandardScaler(), KMeans(n_clusters=k, random_state=seed, n_init=20))
    model.fit(X)
    return model


def benchmark(X, ks=range(2,9), repeats=8, seed=52):
    X = validate(X)
    rng = np.random.default_rng(seed)
    Z = StandardScaler().fit_transform(X)
    # A single correlated Gaussian provides a deliberately cluster-free reference.
    nulls = [rng.multivariate_normal(Z.mean(0), np.cov(Z, rowvar=False), len(Z)) for _ in range(repeats)]
    results, models = [], {}
    for k in ks:
        model = fit_kmeans(X,k,seed); models[k] = model
        labels = model.predict(X)
        sizes = np.bincount(labels, minlength=k)
        seed_aris=[]; subsample_aris=[]; null_scores=[]
        for rep in range(repeats):
            other = fit_kmeans(X,k,seed+rep+1)
            seed_aris.append(adjusted_rand_score(labels,other.predict(X)))
            ix=rng.choice(len(X),size=int(.8*len(X)),replace=False)
            sub = fit_kmeans(X[ix],k,seed+rep+1)
            # Compare on the full fixed cohort; stability is not predictive accuracy.
            subsample_aris.append(adjusted_rand_score(labels,sub.predict(X)))
            null_model=fit_kmeans(nulls[rep],k,seed+rep)
            null_z=null_model[0].transform(nulls[rep])
            null_scores.append(silhouette_score(null_z,null_model.predict(nulls[rep]), sample_size=min(600,len(X)),random_state=seed))
        results.append({'k':k,'silhouette':float(silhouette_score(Z,labels,sample_size=min(600,len(X)),random_state=seed)),
                        'inertia':float(model[-1].inertia_), 'smallest_cluster':int(sizes.min()),
                        'largest_cluster':int(sizes.max()),'seed_ari_mean':float(np.mean(seed_aris)),
                        'subsample_ari_mean':float(np.mean(subsample_aris)),
                        'subsample_ari_min':float(np.min(subsample_aris)),
                        'null_silhouette_mean':float(np.mean(null_scores)),
                        'null_silhouette_sd':float(np.std(null_scores))})
    # Descriptive candidate only: selection on this cohort is not external validation.
    best=max(results,key=lambda r:(r['silhouette'],-r['k']))['k']
    gmm=[]
    for k in range(1,max(ks)+1):
        model=GaussianMixture(n_components=k,n_init=5,random_state=seed,reg_covar=1e-6).fit(Z)
        gmm.append({'components':k,'bic':float(model.bic(Z)), 'aic':float(model.aic(Z)), 'converged':bool(model.converged_)})
    return results, models[best], gmm
