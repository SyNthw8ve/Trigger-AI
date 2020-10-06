from trigger.train.cluster.Processor import Processor

from sklearn.metrics import silhouette_score, calinski_harabasz_score
from typing import Dict, Any

import statistics
from collections import Counter


def eval_cluster(cluster: Processor) -> Dict[str, Any]:
    X, tags = cluster.get_all_instances_with_tags()
    labels = []
    labels_set = set()

    for tag in tags:
        label = cluster.get_cluster_by_tag(tag)
        labels.append(label)
        labels_set.add(label)

    try:

        Ss = silhouette_score(X, labels)
    except:

        Ss = -1.0
    try:
        CHs = calinski_harabasz_score(X, labels)

    except:
        CHs = 0

    num_instances_per_cluster = [
        len(cluster.get_instances_and_tags_in_cluster(label)[1]) for label in labels_set
    ]

    counter = Counter(num_instances_per_cluster)

    return {
        'ss': float(Ss),
        'chs': float(CHs),
        '#clusters': len(labels_set),
        '#instances': len(tags),
        'distribution': counter.most_common(),
        'avg/mean instances / cluster': statistics.mean(num_instances_per_cluster),
        'min instances of any cluster': counter.most_common()[-1:][0][0] if len(counter) > 0 else "0",
        'max instances of any cluster': counter.most_common()[0:1][0][0] if len(counter) > 0 else "0"
    }
