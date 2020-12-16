from typing import List, Type, cast

from trigger.train.cluster.Processor import Processor
from trigger.test.test_runner import TestRunner

from ..instances.user_instance import UserInstance
from ..instances.opening_instance import OpeningInstance

from ..metrics.match import eval_matches_and_cluster

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('test_runner_matches')
logger.setLevel(logging.INFO)


class TestRunnerMatches(TestRunner):

    def __init__(self, processor_class: Type[Processor],
                 param_grid,
                 opening_instances: List[OpeningInstance],
                 user_instances: List[UserInstance],
                 output_path='',
                 output_type='json',
                 skip_done=False):
        super().__init__(processor_class, param_grid,
                         opening_instances, output_path, output_type, skip_done)
        self.user_instances = user_instances

    def run_test(self, processor: Processor, test):
        for opening_instance in self.instances:
            opening_instance = cast(OpeningInstance, opening_instance)
            processor.process(opening_instance.opening.entityId,
                              opening_instance.embedding, opening_instance.opening)

        return eval_matches_and_cluster(processor, self.user_instances)
