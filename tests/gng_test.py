import numpy as np
import logging
import os
import json

from matplotlib import pyplot as plt
from sklearn.metrics import silhouette_score, calinski_harabasz_score
from sklearn.metrics.cluster import adjusted_rand_score
from typing import Tuple, List

from trigger.train.cluster.gstream.gstream import GNG
from util.readers.setup_reader import DataInitializer
from util.test.test_runner import TestRunner


logger = logging.getLogger('matplotlib')
logger.setLevel(logging.WARNING)

users_path = './examples/openings_users/users'
openings_path = './examples/openings_users/openings'
instances_path = './data/instances'
results_path = './results/openings_users'

def test_gng():

    param_grid = {"epsilon_b": [0.001, 0.01],
                    "epsilon_n": [0],
                    "lam": [10, 20, 50],
                    "beta": [0.9995],
                    "alpha": [0.95],
                    "max_age": [20],
                    "off_max_age": [20],
                    "lambda_2": [0.2],
                    "dimensions": [2048],
                    "index_type": ['L2', 'IP'],
                    "nodes_per_cycle": [1, 3, 5]}

    opening_instance_file = 'openings_instances_concat_norm'

    openings_instances_path = os.path.join(
        instances_path, opening_instance_file)

    openings_instances = DataInitializer.read_openings(openings_instances_path, openings_path)
    instances = [opening.embedding for opening in openings_instances]

    gng_tester = TestRunner(GNG, param_grid, instances, './results')
    gng_tester.run_tests()