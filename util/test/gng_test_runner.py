import pandas as pd

from util.test.test_runner import TestRunner
from util.metrics.metrics import eval_cluster
from trigger.train.cluster.gstream.gstream import GNG


class GNGTestRunner(TestRunner):

    def __init__(self, param_grid, instances, output_path='', output_type='json'):

        super().__init__(param_grid, instances, output_path, output_type)

    def run(self, params):

        gng = GNG(**params)

        for instance in self.instances:

            gng.online_fase(instance)

        results = eval_cluster(gng)

        return {'ss': str(results['ss']), 'chs': str(results['chs'])}

