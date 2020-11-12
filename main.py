import os
import pathlib
import pickle

from tests.ecm_tests import test_ecm_operations
from tests.gng_test import test_gng_operations
from util.generators.operation_generator import OperationGenerator
from util.operation import read_operations
from util.readers.setup_reader import DataInitializer

users_path = './examples/openings_users_softskills_confirmed/users'
openings_path = './examples/openings_users_softskills_confirmed/openings'
instances_path = './data/instances_ss_confirmed'
results_path = './results/openings_users'

if __name__ == "__main__":

    # instances_files = [
    #     os.path.join(instances_path, f) for f in os.listdir(instances_path)
    # ]
    #
    # openings_instances_files = [instance_path for instance_path in instances_files if
    #                             instance_path.find("openings") != -1]
    #
    # for openings_instances_path in openings_instances_files:
    #     openings_instances = DataInitializer.read_openings(openings_instances_path, openings_path)
    #
    #     for i in range(5):
    #         directory_path = f"data/operations_update_remove_instances_ss_confirmed/{i}"
    #         pathlib.Path(directory_path).mkdir(parents=True, exist_ok=True)
    #
    #         operations = OperationGenerator.random_from_openings_instances(openings_instances,
    #                                                                        len(openings_instances))
    #         instance_name = os.path.basename(openings_instances_path)
    #         out_path = f"{directory_path}/{instance_name}"
    #         with open(out_path, 'wb') as f:
    #             pickle.dump(operations, f)

    test_gng_operations()
