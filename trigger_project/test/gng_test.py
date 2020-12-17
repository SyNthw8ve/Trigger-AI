import logging
import os
import pathlib

from trigger.train.cluster.gturbo.gturbo import GTurbo

from trigger_project.operation import read_operations
from trigger_project.test.test_runner_matches import TestRunnerMatches
from trigger_project.util.readers.setup_reader import DataInitializer
from trigger_project.test.test_runner_operations_matches import TestRunnerOperationsMatches


logger = logging.getLogger('matplotlib')
logger.setLevel(logging.WARNING)

users_path = './examples/openings_users/users'
openings_path = './examples/openings_users/openings'
instances_path = './data/instances_ss_confirmed'
results_path = './results/openings_users'

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


def test_gng_operations():

    param_grid = {"epsilon_b": [0.01],
                    "epsilon_n": [0],
                    "lam": [500],
                    "beta": [0.9995],
                    "alpha": [0.95],
                    "max_age": [500],
                    "r0": [0.5, 1, 2.5]
                }

    for folder in os.listdir("data/operations_update_remove_instances_ss_confirmed"):
        folder_path = os.path.join("data/operations_update_remove_instances_ss_confirmed", folder)

        logger.info("Doing all instances @ %s", folder_path)

        instances_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path)]

        users_instances_files = [instance_path for instance_path in instances_files if
                                 instance_path.find("users") != -1]

        operations_files = [instance_path for instance_path in instances_files if
                            instance_path.find("operations") != -1]

        for users_instances_path, operations_instances_path in zip(users_instances_files, operations_files):
            logger.info("Doing users + operations @ %s, %s", users_instances_path, operations_instances_path)

            operations = read_operations(operations_instances_path)
            users_instances = DataInitializer.read_users(users_instances_path, users_path)

            instances_folder_name = pathlib.PurePath(folder_path).name

            layer_folder = from_instance_path_to_layer_name(operations_instances_path)

            param_grid['dimensions'] = [1024]

            if "concat" in layer_folder:

                param_grid['dimensions'] = [2048]

            output_path = f'./results/openings_users/operations_update_remove_instances_ss_confirmed/' \
                          f'{layer_folder}/{instances_folder_name}/GTurbo'

            tester = TestRunnerOperationsMatches(
                processor_class=GTurbo,
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