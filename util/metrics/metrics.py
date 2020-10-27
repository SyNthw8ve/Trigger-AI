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

def eval_variability(project: Project):

    embeddings = [opening.embedding for opening in project.openings]

    mean_emb = np.mean(embeddings, axis=0)

    dist_to_mean = cdist([mean_emb], embeddings)
    #dist_to_mean_norm = dist_to_mean / np.linalg.norm(dist_to_mean)

    return np.mean(dist_to_mean)
