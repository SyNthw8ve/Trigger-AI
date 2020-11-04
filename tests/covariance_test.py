import numpy as np
import logging
import os
import json

from matplotlib import pyplot as plt
from sklearn.metrics import silhouette_score, calinski_harabasz_score
from sklearn.metrics.cluster import adjusted_rand_score
from typing import Tuple, List

from trigger.train.cluster.covariance.covariance_cluster import CovarianceCluster
from util.readers.setup_reader import DataInitializer
from util.test.test_runner_matches import TestRunnerMatches

logger = logging.getLogger('matplotlib')
logger.setLevel(logging.WARNING)

users_path = './examples/openings_users/users'
openings_path = './examples/openings_users/openings'
instances_path = './data/instances_ss_confirmed'
results_path = './results/openings_users'

def test_cov():

    param_grid = {"initial_std": [10]
                }

    opening_instance_file = 'openings_instances_no_ss'

    openings_instances_path = os.path.join(instances_path, opening_instance_file)

    openings_instances = DataInitializer.read_openings(openings_instances_path, openings_path)

    users_instance_file = 'users_instances_no_ss'

    users_instances_path = os.path.join(instances_path, users_instance_file)

    users_instances = DataInitializer.read_users(users_instances_path, users_path)

    cov_tester = TestRunnerMatches(CovarianceCluster, param_grid, openings_instances, users_instances, './results/openings_users/instances_ss_confirmed/no_softskills/CovCluster')
    cov_tester.run_tests()