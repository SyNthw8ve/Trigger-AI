from typing import List

from trigger.train.cluster.Processor import Processor
from trigger.train.transformers.user_transformer import UserInstance
from util.metrics.cluster import eval_cluster
from util.metrics.matches import eval_matches


def eval_matches_and_cluster(processor: Processor, users_instances: List[UserInstance]):
    cluster_results = eval_cluster(processor)
    matches_results = eval_matches(processor, users_instances)

    results = cluster_results
    results[matches_results] = matches_results

    return results
