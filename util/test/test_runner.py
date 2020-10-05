from abc import ABC, abstractmethod
from typing import Type

import numpy as np
import logging
import json
import os
import itertools

from trigger.train.cluster.Processor import Processor

from util.metrics.cluster import eval_cluster

class TestRunner(ABC):

    def __init__(self, processor_class: Type[Processor], param_grid, instances, output_path='', output_type='json'):
        self.processor_class = processor_class
        self.param_grid = param_grid
        self.instances = instances
        self.output_path = output_path

        if output_type != 'json' and output_type != 'csv':

            raise Exception("Output file type not supported.")
        
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

            print(test)

            processor = self.processor_class(**test)

            #FIXME: We should have ids here too, but for now the index is good enough
            for i, instance in enumerate(self.instances):
                processor.process(str(i), instance)

            results = eval_cluster(processor)

            if self.output_type == 'json':

                self._save_results_json(processor, results)

            else:

                self._save_results_csv(test, results)


    def _save_results_json(self, processor: Processor, result):

        test_descriptor = {'algorithm': processor.describe(), 'results': result}

        file_name = processor.safe_file_name()

        file_path = os.path.join(self.output_path, F"{file_name}.json")

        with open(file_path, 'w') as f:
            from util.json_util.json_converter import EnhancedJSONEncoder
            json.dump(test_descriptor, f, cls=EnhancedJSONEncoder)

    def _save_results_csv(self, params, result):

        pass
