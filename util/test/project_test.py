import json

from typing import List
from trigger.models.project import Project
from util.metrics.metrics import eval_variability, eval_variability_mahalanobis, eval_variability_cosine
from util.json_util.json_converter import project_to_json


def test_variability(projects: List[Project]):

    projects_json = []

    for project in projects:

        score_cos = eval_variability_cosine(project)
        score_maha = eval_variability_mahalanobis(project)
        score_kur = eval_variability(project)

        score = {'cosine': score_cos, 'mahalanobis': score_maha, 'kurtosis': score_kur["kurtosis"]}

        json_project = project_to_json(project, score)
        projects_json.append(json_project)

    with open("./project_test.json", "w") as f:
        from util.json_util.json_converter import EnhancedJSONEncoder
        json.dump(projects_json, f, cls=EnhancedJSONEncoder)