import logging
import os

import pathlib
from trigger_project.transformers.user_transformer import UserTransformer
from trigger.train.transformers.sentence_embedder import SentenceEmbedder
from trigger_project.transformers.opening_transformer import OpeningTransformer

from trigger.train.cluster.ecm.ecm import ECM

from trigger_project.operation import read_operations
from trigger_project.test.test_runner_matches import TestRunnerMatches
from trigger_project.util.readers.setup_reader import DataInitializer
from trigger_project.test.test_runner_operations_matches import TestRunnerOperationsMatches

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ecm_tests')
logger.setLevel(logging.INFO)

users_path = './examples/openings_users/users'
openings_path = './examples/openings_users/openings'

instances_paths = [
    './data/instances',
    './data/instances_ss_confirmed',
    './data/save'
]


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


def test_ecm_matches_instances():
    param_grid = {
        "distance_threshold": [0.001, 0.01, 0.1, 0.3, 0.5,
                               0.7, 0.9, 1, 1.2, 1.4, 1.5]
    }

    for instances_path in instances_paths:

        logger.info("Doing all instances @ %s", instances_path)

        instances_files = [
            os.path.join(instances_path, f)
            for f in os.listdir(instances_path)
            if os.path.isfile(os.path.join(instances_path, f))
        ]

        users_instances_files = sorted([
            instance_path
            for instance_path in instances_files
            if  instance_path.find("users") != -1
        ])

        openings_instances_files = sorted([
            instance_path
            for instance_path in instances_files
            if instance_path.find("openings") != -1
        ])

        for users_instances_path, openings_instances_path in zip(users_instances_files, openings_instances_files):
            logger.info("Doing users + openings instances @ %s, %s",
                        users_instances_path, openings_instances_path)

            openings_instances = DataInitializer.read_openings(openings_instances_path, openings_path)
            users_instances = DataInitializer.read_users(users_instances_path, users_path)

            instances_folder_name = pathlib.PurePath(instances_path).name

            layer_folder = from_instance_path_to_layer_name(openings_instances_path)

            gng_tester = TestRunnerMatches(ECM, param_grid, openings_instances, users_instances,
                                           f'./results/openings_users/{instances_folder_name}/{layer_folder}/ECM',
                                           'json', False)
            gng_tester.run_tests()


def test_ecm_operations():
    param_grid = {
        "distance_threshold": [0.4, 0.5, 0.6, 0.7, 0.8]
    }

    for folder in os.listdir("data/operations_update_remove_instances_ss_confirmed"):
        folder_path = os.path.join("data/operations_update_remove_instances_ss_confirmed", folder)

        logger.info("Doing all instances @ %s", folder_path)

        instances_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path)]

        users_instances_files = sorted([instance_path for instance_path in instances_files if
                                 instance_path.find("users") != -1])

        operations_files = sorted([instance_path for instance_path in instances_files if
                            instance_path.find("operations") != -1])

        for users_instances_path, operations_instances_path in zip(users_instances_files, operations_files):
            logger.info("Doing users + operations @ %s, %s", users_instances_path, operations_instances_path)

            operations = read_operations(operations_instances_path)
            
            users_instances = DataInitializer.read_users(users_instances_path, users_path)

            instances_folder_name = pathlib.PurePath(folder_path).name

            layer_folder = from_instance_path_to_layer_name(operations_instances_path)

            output_path = f'./results/openings_users/operations_update_remove_instances_ss_confirmed/' \
                          f'{layer_folder}/{instances_folder_name}/ECM'

            tester = TestRunnerOperationsMatches(
                processor_class=ECM,
                param_grid=param_grid,
                operations=operations,
                user_instances=users_instances,
                calculate_score_frequency=100,
                output_path=output_path,
                output_type='json',
                include_individual_matches=False,
                skip_done=False
            )

            tester.run_tests()