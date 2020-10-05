from trigger.train.cluster.Processor import Processor

from sklearn.metrics import silhouette_score, calinski_harabasz_score
from typing import Dict

def eval_cluster(cluster: Processor) -> Dict[str, str]:

    X, tags = cluster.get_all_instances_with_tags()
    labels = []

    for tag in tags:
        labels.append(cluster.get_cluster_by_tag(tag))

    try:

        Ss = silhouette_score(X, labels)
    except:

        Ss = -1.0
    try:
        CHs = calinski_harabasz_score(X, labels)

    except:
        CHs = 0

    return {'ss': str(Ss), 'chs': str(CHs)}