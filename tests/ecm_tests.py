import logging
import os

from trigger.train.cluster.ecm.ecm import ECM
from util.readers.setup_reader import DataInitializer
from util.test.test_runner import TestRunner

logger = logging.getLogger('test_ecm')
logger.setLevel(logging.WARNING)

users_path = './examples/openings_users/users'
openings_path = './examples/openings_users/openings'
instances_path = './data/instances'
results_path = './results/openings_users'


def test_ecm():

    param_grid = {
        "distance_threshold":
            [0.001,
             0.005,
             0.010,
             0.020,
             0.050,
             0.1,
             0.2,
             0.5,
             1,
             1.2,
             1.5,
             1.5,
             2,
             2.2,
             2.5,
             4,
             4.2,
             4.5,
             5,
             5.2,
             5.5,
             6,
             6.2,
             6.5,
             7],
    }

    opening_instance_file = 'openings_instances_concat_norm'

    openings_instances_path = os.path.join(
        instances_path, opening_instance_file)

    openings_instances = DataInitializer.read_openings(openings_instances_path, openings_path)
    instances = [opening.embedding for opening in openings_instances]

    gng_tester = TestRunner(ECM, param_grid, instances, './results/openings_users/concat_layer_norm')
    gng_tester.run_tests()
