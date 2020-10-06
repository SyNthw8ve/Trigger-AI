from pathlib import Path
from trigger.train.transformers.user_transformer import UserInstance
from trigger.train.transformers.opening_transformer import Opening, OpeningInstance
from typing import List, Type, cast

import json
import itertools
import os
import logging

from trigger.train.cluster.Processor import Processor

from util.metrics.cluster import eval_cluster
from util.metrics.matches import eval_matches
from util.test.test_runner import TestRunner

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
                         opening_instances, output_path, output_type)
        self.user_instances = user_instances
        self.skip_done = skip_done

    def run_tests(self):

        for test in self.tests:

            logger.info("Started test with params %s", str(test))

            processor = self.processor_class(**test)

            file_path = self._get_file_path(processor, self.output_type)

            if self.skip_done and Path(file_path).exists():
                logger.info(
                    "Skipping test with output at %s. (file exists)", file_path)
                continue

            for opening_instance in self.instances:
                opening_instance = cast(OpeningInstance, opening_instance)
                processor.process(opening_instance.opening.entityId,
                                  opening_instance.embedding, opening_instance.opening)

            print("Computing results...")

            results = eval_cluster(processor)
            results['matches_results'] = eval_matches(
                processor, self.user_instances)

            if self.output_type == 'json':

                self._save_results_json(processor, results)

            else:

                self._save_results_csv(test, results)

    def _get_file_path(self, processor: Processor, output_type: str):
        file_name = processor.safe_file_name()
        return os.path.join(self.output_path, F"{file_name}.{output_type}")

    def _save_results_json(self, processor: Processor, result):

        test_descriptor = {
            'algorithm': processor.describe(),
            'results': result
        }

        file_path = self._get_file_path(processor, 'json')

        print(f"Saving results to {file_path}...")

        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w') as f:
            from util.json_util.json_converter import EnhancedJSONEncoder
            json.dump(test_descriptor, f, cls=EnhancedJSONEncoder)

    def _save_results_csv(self, params, result):

        pass
