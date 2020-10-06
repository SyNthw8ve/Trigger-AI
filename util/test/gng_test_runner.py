import pandas as pd

from util.test.test_runner import TestRunner
from trigger.train.cluster.gturbo.gturbo import GTurbo


class GNGTestRunner():

    def __init__(self, param_grid, instances, output_path='', output_type='json'):

        super().__init__(param_grid, instances, output_path, output_type)

