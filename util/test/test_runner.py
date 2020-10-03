from abc import ABC

import numpy as np
import logging
import json
import os

class TestRunner(ABC):

    def __init__(self, param_grid, instances, output_path='', output_type='json'):
        
        self.param_grid = param_grid
        self.instances = instances
        self.output_path = output_path

        if output_type != 'json' and output_type != 'csv':

            raise Exception("Output file type not supported.")
        
        self.output_type = output_type
        self.tests = self._build_tests()

    def _build_tests(self):

        test_keys = self.param_grid.keys()

        test_values = tuple(self.param_grid.values())
        test_combinations = np.array(np.meshgrid(*test_values)).T.reshape(-1, len(test_values))

        test_items = [dict(zip(test_keys, test_item)) for test_item in test_combinations]

        return test_items

    def run_tests(self):

        for test in self.tests:

            results = self.run(test)

            if self.output_type == 'json':

                self._save_results_json(test, results)

            else:

                self._save_results_csv(test, results)

    @abstractmethod
    def run(self, params):

        pass

    def _save_results_json(self, params, result):

        test_descriptor = {'params': params, 'results': result}

        file_name = self._gen_name(params)

        file_path = os.path.join(self.output_path, F"{file_name}.json")

        with open(file_path, 'w') as f:

            json.dump(test_descriptor, f)

    def _save_results_csv(self, params, result):

        pass

    def _gen_name(self, params):

        name_parts = [f"{key}={value}" for key, value in params.items()]

        return ":".join(name_parts)
    