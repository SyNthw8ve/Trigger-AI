import logging
import os
from typing import List

from trigger.models.match import Match
from trigger.train.transformers.opening_transformer import OpeningInstance
from trigger.train.transformers.user_transformer import UserInstance
from util.metrics.matches import computeScore, eval_cluster
from util.readers.setup_reader import DataInitializer
from tests.gng_test import test_gng

from trigger.train.cluster.gturbo.gturbo import GTurbo

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

    # test_gng()

    user_instance_file = f'users_instances_concat'
    opening_instance_file = f'openings_instances_concat'

    openings_instances_path = os.path.join(
        instances_path, opening_instance_file)

    users_instances_path = os.path.join(instances_path, user_instance_file)
    users_instances = DataInitializer.read_users(
        users_instances_path, users_path, concat_layer='concat', normed=True)

    logging.info("Users instances complete.")

    openings_instances_path = os.path.join(
        instances_path, opening_instance_file)

    openings_instances = DataInitializer.read_openings(
        openings_instances_path, openings_path, concat_layer='concat', normed=True)

    logging.info("Openings instances complete.")

    gturbo = GTurbo(epsilon_b=0.001, epsilon_n=0, lam=200, beta=0.995,
                    alpha=0.95, max_age=200, r0=3, dimensions=2048)


    """ logging.info("Inserting Openings in Birch")

    birch = Birch()

    instances = []

    for opening_instance in openings_instances[:200]:

        instances.append(opening_instance.embedding)

    logging.info("Birch Agent Training")

    threshold = 0.5
    branching_factor = 50
    dimension = 1024

    collect_env = BirchDiscreteEnvironment(
        initial_threshold=threshold, initial_branching=branching_factor, instances=instances, dimension=dimension)
    eval_env = BirchDiscreteEnvironment(
        initial_threshold=threshold, initial_branching=branching_factor, instances=instances, dimension=dimension)

    q_network = QNetwork(collect_env, eval_env)

    q_network.train('test_policy', 10, 1) """
