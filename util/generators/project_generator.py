import random

from trigger.models.project import Project
from typing import List
from util.readers.setup_reader import DataInitializer

class ProjectGenerator:

    @classmethod
    def projects_from_file(instances_path: str, path: str, num_projects=1, min_openings_per_project=1, max_openings_per_project=1) -> List[Project]:

        openings = DataInitializer.read_openings(
            openings_instances_path=instances_path, openings_path=path)

        projects = []
        for _ in range(num_projects):

            num_openings = random.randint(
                min_openings_per_project, max_openings_per_project)

            project_openings = random.sample(openings, num_openings)

            projects.append(Project(project_openings))

        return projects
