from typing import List, Type, cast

from ..metrics.match import eval_matches_and_cluster
from ..operation import Operation, OperationType
from ..instances.user_instance import UserInstance

from trigger.train.cluster.Processor import Processor
from trigger.test.test_runner import TestRunner

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('test_runner_matches')
logger.setLevel(logging.INFO)


class TestRunnerOperationsMatches(TestRunner):

    def __init__(self, processor_class: Type[Processor],
                 param_grid,
                 operations: List[Operation],
                 user_instances: List[UserInstance],
                 calculate_score_frequency: int,
                 output_path='',
                 output_type='json',
                 include_individual_matches=True,
                 skip_done=False):
        super().__init__(processor_class, param_grid,
                         operations, output_path, output_type, skip_done)
        self.include_individual_matches = include_individual_matches
        self.calculate_score_frequency = calculate_score_frequency
        self.user_instances = user_instances

    def run_test(self, processor: Processor, test):

        results = {}

        for i, operation in enumerate(self.instances):
            operation = cast(Operation, operation)
            if operation.type == OperationType.NEW_OPENING:
                opening_instance = operation.opening_instance
                opening = opening_instance.opening
                tag = operation.opening_instance_tag

                processor.process(tag, opening_instance.embedding, opening)

            elif operation.type == OperationType.REMOVE_OPENING:
                tag = operation.opening_instance_tag

                processor.remove(tag)

            elif operation.type == OperationType.UPDATE_OPENING:
                opening_instance = operation.opening_instance
                opening = opening_instance.opening
                tag = operation.opening_instance_tag

                processor.update(tag, opening_instance.embedding, opening)

            if i > 0 and i % self.calculate_score_frequency == 0 or i == len(self.instances) - 1:
                these_results = eval_matches_and_cluster(processor, self.user_instances)
                if not self.include_individual_matches:
                    del these_results['matches_results']['by_user']
                results[i] = these_results

        return results
