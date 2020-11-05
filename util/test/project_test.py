import json

from typing import List
from trigger.models.project import Project
from util.metrics.metrics import eval_variability, eval_variability_mahalanobis
from util.json_util.json_converter import project_to_json


def test_variability(projects: List[Project]):

    projects_json = []

    for project in projects:

        score = eval_variability_mahalanobis(project)

        json_project = project_to_json(project, score)
        projects_json.append(json_project)

    with open("./project_test.json", "w") as f:
        from util.json_util.json_converter import EnhancedJSONEncoder
        json.dump(projects_json, f, cls=EnhancedJSONEncoder)