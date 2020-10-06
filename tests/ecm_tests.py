import logging
import os
from util.test.test_runner_matches import TestRunnerMatches

import pathlib

from trigger.train.cluster.ecm.ecm import ECM
from util.readers.setup_reader import DataInitializer

logging.basicConfig(level = logging.INFO)
logger = logging.getLogger('ecm_tests')
logger.setLevel(logging.INFO)

users_path = './examples/openings_users/users'
openings_path = './examples/openings_users/openings'

instances_paths = ['./data/instances', './data/instances_ss_confirmed', './data/save']

def test_ecm():

    param_grid = {
        "distance_threshold":
            [0.001,
             0.005,
             0.01,
             0.02,
             0.05,
             0.1,
             0.15,
             0.2,
             0.25,
             0.3,
             0.4,
             0.5,
             0.6,
             0.7,
             0.8,
             0.9,
             1,
             1.1,
             1.2,
             1.3,
             1.4,
             1.5]
    }

    for instances_path in instances_paths:

        logger.info("Doing all instances @ %s", instances_path)

        instances_files = [os.path.join(instances_path, f) for f in os.listdir(
            instances_path) if os.path.isfile(os.path.join(instances_path, f))]

        users_instances_files = [instance_path for instance_path in instances_files if instance_path.find("users") != -1]

        openings_instances_files = [instance_path for instance_path in instances_files if
                                    instance_path.find("openings") != -1]

        for users_instances_path, openings_instances_path in zip(users_instances_files, openings_instances_files):

            logger.info("Doing users + openings instances @ %s, %s", users_instances_path, openings_instances_path)

            openings_instances = DataInitializer.read_openings(openings_instances_path, openings_path)
            users_instances = DataInitializer.read_users(users_instances_path, users_path)

            def from_instance_path_to_layer_name(instance_path: str) -> str:
                if instance_path.find("avg_norm") != -1:
                    return "avg_layer_norm"

                if instance_path.find("avg") != -1:
                    return "avg_layer"

                if instance_path.find("concat_norm") != -1:
                    return "concat_layer_norm"

                if instance_path.find("concat") != -1:
                    return "concat_layer"

                if instance_path.find("no_ss") != -1:
                    return "no_softskills"

                return "?"

            instances_folder_name = pathlib.PurePath(instances_path).name

            layer_folder = from_instance_path_to_layer_name(openings_instances_path)

            gng_tester = TestRunnerMatches(ECM, param_grid, openings_instances, users_instances, f'./results/openings_users/{instances_folder_name}/{layer_folder}/ECM', 'json', False)
            gng_tester.run_tests()
