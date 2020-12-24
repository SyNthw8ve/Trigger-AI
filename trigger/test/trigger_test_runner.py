from trigger.trigger_interface import TriggerInterface
from interference.test.test_operations_runner import TestRunner
from interference.interface import Interface

class TriggerTestRunner(TestRunner):

    def init_inferface(self, params) -> Interface:
        processor = self.processor_class(**params)
        return TriggerInterface(processor, self.transformers, self.scoring_calculator)