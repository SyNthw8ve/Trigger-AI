import json

from typing import List
from ..models.project import Project
from ..metrics.project import eval_variability, eval_variability_mahalanobis, eval_variability_cosine, eval_variability_cosine_to_mean


def test_variability(projects: List[Project]):

    projects_json = []

    for project in projects:

        score_cos = eval_variability_cosine(project)
        score_maha = eval_variability_mahalanobis(project)
        score_kur = eval_variability(project)
        score_cos_mean = eval_variability_cosine_to_mean(project)

        json_project = {
            "project": project,
            'cosine': score_cos,
            'cosine_to_mean': score_cos_mean,
            'mahalanobis': score_maha,
            'kurtosis': score_kur["kurtosis"]
        }

        projects_json.append(json_project)

    with open("./project_test.json", "w") as f:
        from interference.util.json_encoder import EnhancedJSONEncoder
        json.dump(projects_json, f, cls=EnhancedJSONEncoder)
