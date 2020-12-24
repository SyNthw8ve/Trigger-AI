from trigger_project.trigger_interface import TriggerInterface
from trigger.test.test_operations_runner import TestRunner
from trigger.interface import Interface

class TriggerTestRunner(TestRunner):

    def init_inferface(self, params) -> Interface:
        processor = self.processor_class(**params)
        return TriggerInterface(processor, self.transformers, self.scoring_calculator)