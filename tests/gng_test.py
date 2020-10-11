import numpy as np
import logging
import os
import json

from matplotlib import pyplot as plt
from sklearn.metrics import silhouette_score, calinski_harabasz_score
from sklearn.metrics.cluster import adjusted_rand_score
from typing import Tuple, List

from trigger.train.cluster.gturbo.gturbo import GTurbo
from util.readers.setup_reader import DataInitializer
from util.test.test_runner_matches import TestRunnerMatches


logger = logging.getLogger('matplotlib')
logger.setLevel(logging.WARNING)

users_path = './examples/openings_users/users'
openings_path = './examples/openings_users/openings'
instances_path = './data/instances_ss_confirmed'
results_path = './results/openings_users'

def test_gng():

    param_grid = {"epsilon_b": [0.001, 0.01],
                    "epsilon_n": [0],
                    "lam": [200, 500],
                    "beta": [0.9995],
                    "alpha": [0.95],
                    "max_age": [200, 500],
                    "dimensions": [1024],
                    "r0": [0.5, 1, 2.5, 5, 8]
                }

    opening_instance_file = 'openings_instances_no_ss_norm'

    openings_instances_path = os.path.join(instances_path, opening_instance_file)

    openings_instances = DataInitializer.read_openings(openings_instances_path, openings_path)

    users_instance_file = 'users_instances_no_ss_norm'

    users_instances_path = os.path.join(instances_path, users_instance_file)

    users_instances = DataInitializer.read_users(users_instances_path, users_path)

    gng_tester = TestRunnerMatches(GTurbo, param_grid, openings_instances, users_instances, './results/openings_users/instances_ss_confirmed/no_softskills_norm/GTurbo')
    gng_tester.run_tests()