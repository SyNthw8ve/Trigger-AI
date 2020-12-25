from trigger.scoring import TriggerScoring
from trigger.evaluation.matches import eval_matches
from typing import Any, List, Optional, cast
from interference.interface import Interface
from interference.operations import CalculateMatchesInfo
from interference.scoring import Scoring

class TriggerInterface(Interface):

    def _evaluate_matches_inner(self, values: List[CalculateMatchesInfo]):

        instances, scorings = self._calculate_operation_matches_inner(values)
        # Don't worry, they are trigger scorings :)
        scorings = cast(List[List[TriggerScoring]], scorings)
        return eval_matches(instances, scorings)

    def get_matches_for(self, transformer_key: str, value: Any) -> Optional[List[TriggerScoring]]:
        base = super().get_matches_for(transformer_key, value)
        return cast(Optional[List[TriggerScoring]], base)

    def calculate_scoring_between_value_and_tag(self, transformer_key: str, value: Any, tag: str) -> Optional[TriggerScoring]:
        base = super().calculate_scoring_between_value_and_tag(transformer_key, value, tag)
        return cast(Optional[TriggerScoring], base)