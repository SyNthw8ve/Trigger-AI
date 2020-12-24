from trigger.scoring import TriggerScoring
from trigger.evaluation.matches import eval_matches
from typing import List, cast
from interference.interface import Interface
from interference.operations import CalculateMatchesInfo

class TriggerInterface(Interface):

    def _evaluate_matches_inner(self, values: List[CalculateMatchesInfo]):

        instances, scorings = self._calculate_operation_matches_inner(values)
        # Don't worry, they are trigger scorings :)
        scorings = cast(List[List[TriggerScoring]], scorings)
        return eval_matches(instances, scorings)