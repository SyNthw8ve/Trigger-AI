import os
import pprint
import logging
import json
import copy
import numpy as np
import tensorflow as tf

from typing import List, Tuple

from trigger.models.Match import Match

from trigger.models.opening import Opening
from trigger.models.hardskill import Hardskill
from trigger.models.language import Language
from trigger.models.user import User

from trigger.recommend import smart
from trigger.recommend.controller import Controller
from trigger.recommend.clusters import Clusters
from trigger.recommend.opening_transformer import OpeningTransformer
from trigger.recommend.skill_transformers.soft_skill_transformer import SoftskillTransformer

from trigger.recommend.user_transformer import UserTransformer

from util.readers.reader import DataReaderOpenings, DataReaderUsers
from util.json_util.json_converter import user_to_json, opening_to_json
from util.metrics.metrics import eval_cluster, computeScore

from trigger.train.transformers.input_transformer import SentenceEmbedder
from trigger.train.transformers.user_transformer import UserInstance
from trigger.train.transformers.opening_transformer import OpeningInstance

from trigger.train.cluster.birch.birch import Birch
from trigger.train.reinforcement_tuning.environments.train.birch_cont_env import BirchContinuousEnvironment
from trigger.train.reinforcement_tuning.environments.train.birch_disc_env import BirchDiscreteEnvironment

from trigger.train.reinforcement_tuning.environments.online.birch_cont_env import OnlineBirchContinuosEnvironment

from tf_agents.environments.py_environment import PyEnvironment
from tf_agents.environments import tf_py_environment
from trigger.train.reinforcement_tuning.networks.actor_critic import ActorCriticNetwork
from trigger.train.reinforcement_tuning.networks.q_network import QNetwork

from util.readers.setup_reader import DataInitializer
from tests.gng_test import test_gng

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

    #test_gng()

    user_instance_file = f'users_instances_avg'
    opening_instance_file = f'no_ss_openings_instances'
    
    openings_instances_path = os.path.join(
        instances_path, opening_instance_file)

    users_instances_path = os.path.join(instances_path, user_instance_file)
    users_instances = DataInitializer.read_users(users_instances_path, users_path)

    logging.info("Users instances complete.")

    openings_instances_path = os.path.join(
        instances_path, opening_instance_file)

    openings_instances = DataInitializer.read_openings(openings_instances_path, openings_path)

    logging.info("Openings instances complete.")

    logging.info("Inserting Openings in Birch")

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

    q_network.train('test_policy', 10, 1)
