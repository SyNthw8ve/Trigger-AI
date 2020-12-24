import numpy as np
from scipy.spatial.distance import cdist, mahalanobis
from scipy.stats import kurtosis

from ..models.project import Project 

def eval_variability_cosine_to_mean(project: Project):

    if len(project.openings) == 1:

        return 0.0

    embeddings = [opening.embedding for opening in project.openings]
    mean_embedding = np.mean(embeddings, axis=0)

    distances = [cdist([embedding], [mean_embedding], 'cosine')[0][0] for embedding in embeddings]

    return np.mean(distances)

def eval_variability_cosine(project: Project):

    if len(project.openings) == 1:

        return 0.0

    embeddings = [opening.embedding for opening in project.openings]

    distances = []

    for i in range(len(embeddings)):

        t_embedding = embeddings[i]

        for j in range(i + 1, len(embeddings)):

            c_embedding = embeddings[j]

            distances.append(cdist([t_embedding], [c_embedding], 'cosine')[0][0])

    return np.mean(distances)

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

    distances = np.array(distances)

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
