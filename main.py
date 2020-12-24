from trigger_project.test.trigger_test_runner import TriggerTestRunner
from trigger_project.scoring import TriggerScoringCalculator, TriggerScoringOptions
from trigger_project.operation import read_operations

from data.operations_instances_ss_confirmed import fetch_operations_files

from trigger.clusters.ecm import ECM

if __name__ == "__main__":

    operations_files = fetch_operations_files()

    for operations_file in operations_files:
        test_runner = TriggerTestRunner(
            processor_class=ECM,
            param_grid={ "distance_threshold": [0.5, 1.] },
            operations=read_operations(operations_file.full_path),
            scoring_calculator=TriggerScoringCalculator(TriggerScoringOptions(score_to_be_match=0.2)),
            output_base_folder=f"results/openings_users/operations/{operations_file.test_subpath}/"
        )
        test_runner.run_tests()