import numpy as np

from typing import List

from trigger.train.cluster.Processor import Processor
from trigger.train.transformers.user_transformer import UserInstance
from util.metrics.cluster import eval_cluster
from util.metrics.matches import eval_matches

from trigger.models.project import Project

from scipy.spatial.distance import cdist, mahalanobis
from scipy.stats import kurtosis


def eval_matches_and_cluster(processor: Processor, users_instances: List[UserInstance]):
    cluster_results = eval_cluster(processor)
    matches_results = eval_matches(processor, users_instances)

    results = cluster_results
    results['matches_results'] = matches_results

    return results


def eval_variability_mahalanobis(project: Project):

    if len(project.openings) == 1:

        return 0.0

    embeddings = [opening.embedding for opening in project.openings]
    embeddings_transposed = [opening.embedding.reshape(
        (1024, 1)) for opening in project.openings]

    observations = np.hstack(embeddings_transposed)
    cov_matrix = np.cov(observations)

    distances = []

    for i in range(len(embeddings)):

        t_embedding = embeddings[i]

        for j in range(i + 1, len(embeddings)):

            c_embedding = embeddings[j]

            distances.append(mahalanobis(t_embedding, c_embedding, cov_matrix))

    mean_distance = np.mean(distances)

    return mean_distance


def eval_variability(project: Project):

    embeddings = [opening.embedding for opening in project.openings]

    mean_emb = np.mean(embeddings, axis=0)

    dist_to_mean = cdist([mean_emb], embeddings)

    std = np.std(dist_to_mean)
    mean = np.mean(dist_to_mean)
    normed_kurtosis = 0
    mean_std_ratio = 0

    if mean != 0 and std != 0:
        mean_std_ratio = std/mean
        normed_kurtosis = (-kurtosis(dist_to_mean[0]) + 3)/6

    return {'std': std, 'mean': mean, 'mean-std-ration': mean_std_ratio, 'kurtosis': normed_kurtosis}
