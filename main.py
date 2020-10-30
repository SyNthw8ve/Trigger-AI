import logging
import os
from typing import List

from trigger.models.match import Match
from trigger.train.transformers.opening_transformer import OpeningInstance
from trigger.train.transformers.user_transformer import UserInstance
from trigger.train.transformers.input_transformer import SentenceEmbedder

from util.metrics.matches import computeScore
from util.readers.setup_reader import DataInitializer
from data_analysis.analysis import load_data, skills_count_openings, skills_count_users, dulicate

from trigger.train.cluster.gturbo.gturbo import GTurbo

from util.generators.project_generator import ProjectGenerator
from util.test.project_test import test_variability

users_path = './examples/openings_users_softskills_confirmed/users'
openings_path = './examples/openings_users_softskills_confirmed/openings'
instances_path = './data/instances_ss_confirmed'
results_path = './results/openings_users'


def getOpenings(id: int, user: UserInstance, openings: List[OpeningInstance], threshold: float) -> List[Match]:

    openingsOfInterest = [
        openingInstance for openingInstance in openings if openingInstance.cluster_index == id]

    return [Match(user.user, computeScore(user, openingInstance), openingInstance.opening)
            for openingInstance in openingsOfInterest
            if computeScore(user, openingInstance) >= threshold]


if __name__ == "__main__":

    opening_instance_file = 'openings_instances_no_ss'

    openings_instances_path = os.path.join(
        instances_path, opening_instance_file)

    projects = ProjectGenerator.projects_from_file(
        instances_path=openings_instances_path, path=openings_path, num_projects=3, min_openings_per_project=5, max_openings_per_project=5)

    test_variability(projects)

    """ opening_instance_file = 'openings_instances_avg'

    openings_instances_path = os.path.join(
        instances_path, opening_instance_file)

    openings_instances = DataInitializer.read_openings(
        openings_instances_path, openings_path)

    gturbo = GTurbo(epsilon_b=0.01, epsilon_n=0, lam=200, beta=0.9995,
                    alpha=0.95, max_age=200, r0=0.5, dimensions=1024)

    for opening_instance in openings_instances:

        gturbo.turbo_step(opening_instance.opening.entityId, opening_instance.embedding)

    print(gturbo.compute_cluster_score()) """

    """ users_path = './examples/openings_users_softskills_confirmed/users'
    openings_path = './examples/openings_users_softskills_confirmed/openings'

    users_file = os.path.join(users_path, 'users_0.txt')
    openings_file = os.path.join(openings_path, 'openings_0.txt')

    users, openings = load_data(users_file, openings_file)

    dulicate(users) """
