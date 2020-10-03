from sklearn.metrics import silhouette_score, calinski_harabasz_score
from trigger.train.cluster.birch.birch import Birch

def eval_cluster(birch: Birch):

    X = birch.instances
    labels = []
    results = {'ss': 0, 'chs': 0}

    for x in X:

        labels.append(birch.index_of_cluster_containing(x))

    try:
        results['ss'] = silhouette_score(X, labels)
    except:
        results['ss'] = 0

    try:
        results['chs'] = calinski_harabasz_score(X, labels)
    except:
        results['chs'] = 0

    return results

