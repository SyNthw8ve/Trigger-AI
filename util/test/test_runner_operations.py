from util.metrics.cluster import eval_cluster
from util.operation import Operation, OperationType
from trigger.train.transformers.user_transformer import UserInstance
from typing import List, Type, cast

from trigger.train.cluster.Processor import Processor

from util.test.test_runner import TestRunner

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('test_runner_matches')
logger.setLevel(logging.INFO)


class TestRunnerOperations(TestRunner):

    def __init__(self, processor_class: Type[Processor],
                 param_grid,
                 operations: List[Operation],
                 calculate_score_frequency: int,
                 output_path='',
                 output_type='json',
                 skip_done=False):
        super().__init__(processor_class, param_grid,
                         operations, output_path, output_type, skip_done)
        self.calculate_score_frequency = calculate_score_frequency

    def run_test(self, processor: Processor, test):

        results = {}

        for i, operation in enumerate(self.instances):
            operation = cast(Operation, operation)
            if operation.type == OperationType.NEW_OPENING:
                opening_instance = operation.opening_instance
                opening = opening_instance.opening
                tag = opening.entityId
                processor.process(tag, opening_instance.embedding, opening)

            elif operation.type == OperationType.REMOVE_OPENING:
                opening_instance = operation.opening_instance
                opening = opening_instance.opening
                tag = opening.entityId
                processor.remove(tag)

            elif operation.type == OperationType.UPDATE_OPENING:
                opening_instance = operation.opening_instance
                opening = opening_instance.opening
                tag = opening.entityId
                processor.update(tag, opening_instance.embedding, opening)

            if i % self.calculate_score_frequency == 0:
                results[i] = eval_cluster(processor)

        return results
