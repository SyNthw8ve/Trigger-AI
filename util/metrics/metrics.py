import numpy as np

from trigger.train.transformers.opening_transformer import OpeningInstance
from typing import List

from trigger.train.cluster.Processor import Processor
from trigger.train.transformers.user_transformer import UserInstance
from util.metrics.cluster import eval_cluster
from util.metrics.matches import eval_matches

from trigger.models.project import Project

from scipy.spatial.distance import cosine
from scipy.spatial.distance import cdist

def eval_matches_and_cluster(processor: Processor, users_instances: List[UserInstance]):
    cluster_results = eval_cluster(processor)
    matches_results = eval_matches(processor, users_instances)

    results = cluster_results
    results['matches_results'] = matches_results

    return results

def _get_distances(openings: List[OpeningInstance], metric='cos'):

    similarities = []

    for i in range(len(openings) - 1):

        test_instance = openings[openings[i]].embedding

        for j in range(i + 1, len(openings)):

            compare_instance = openings[openings[j]].embedding

            cos_sim = 1 - cosine(test_instance, compare_instance)
            similarities.append(cos_sim)

    return similarities

def eval_variability(project: Project):

    similarities = _get_distances(project.openings)

    mean_sim = np.mean(similarities)
    var_sim = np.var(similarities)

    return var_sim / mean_sim
