from pathlib import Path
from trigger_project.util.json_util.json_converter import EnhancedJSONEncoder
from typing import Any, Dict, List, Type

import logging

import json
import itertools
import os

from trigger.train.cluster.Processor import Processor

from ..metrics.cluster import eval_cluster

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('test_runner')
logger.setLevel(logging.INFO)


class TestRunner:

    def __init__(
        self,
        processor_class: Type[Processor],
        param_grid: Dict[str, Any],
        instances: List[Any],
        output_path:str='',
        output_type:str='json',
        skip_done:bool=False
    ):
        self.processor_class = processor_class
        self.param_grid = param_grid
        self.instances = instances
        self.output_path = output_path
        self.skip_done = skip_done

        if output_type != 'json' and output_type != 'csv':
            raise ValueError("Output file type not supported.")

        self.output_type = output_type
        self.tests = self._build_tests()

    def _build_tests(self):

        test_keys = self.param_grid.keys()

        test_values = self.param_grid.values()
        test_combinations = itertools.product(*test_values)

        test_items = [dict(zip(test_keys, test_item)) for test_item in test_combinations]

        return test_items

    def run_tests(self):

        for test in self.tests:

            processor = self.processor_class(**test)

            file_path = self._get_file_path(processor, self.output_type)

            if self.skip_done and Path(file_path).exists():
                logger.info("Skipping test with params %s and output at %s. (file exists)", str(test), file_path)
                continue

            logger.info("Started test with params %s", str(test))

            results = self.run_test(processor, test)

            if self.output_type == 'json':

                self._save_results_json(processor, test, results)

            else:

                self._save_results_csv(test, results)

    def run_test(self, processor: Processor, test):
        # FIXME: We should have ids here too, but for now the index is good enough
        for i, instance in enumerate(self.instances):
            processor.process(str(i), instance)

        return eval_cluster(processor)

    def _get_file_path(self, processor: Processor, output_type: str):
        file_name = processor.safe_file_name()
        return os.path.join(self.output_path, F"{file_name}.{output_type}")

    def _save_results_json(self, processor: Processor, test, result):

        test_descriptor = {'algorithm': processor.describe(), 'results': result}

        file_path = self._get_file_path(processor, 'json')

        logger.info(f"Saving results to %s...", file_path)

        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w') as f:
            json.dump(test_descriptor, f, cls=EnhancedJSONEncoder)

    def _save_results_csv(self, params, result):
        pass
