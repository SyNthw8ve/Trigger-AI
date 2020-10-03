import pprint
import numpy as np
import pickle as pk
import logging
import json

from matplotlib import pyplot as plt
from trigger.train.cluster.gstream.gstream import GNG
from sklearn.metrics import silhouette_score, calinski_harabasz_score
from sklearn.metrics.cluster import adjusted_rand_score
from typing import Tuple, List
from util.test.gng_test_runner import GNGTestRunner

logger = logging.getLogger('matplotlib')
logger.setLevel(logging.WARNING)

users_path = './examples/openings_users/users'
openings_path = './examples/openings_users/openings'
instances_path = './data/instances'
results_path = './results/openings_users'

if __name__ == "__main__":

    param_grid = {"epsilon_b": [0.001, 0.01, 0.1],
                  "epsilon_n": [0],
                  "lam": [200, 100],
                  "beta": [0.9995],
                  "alpha": [0.95],
                  "max_age": [200, 100],
                  "off_max_age": [200],
                  "lambda_2": [0.2, 0.4],
                  "dimensions": [1024],
                  "index_type": ['L2', 'IP'],
                  "nodes_per_cycle": [1, 3, 5]}

    
