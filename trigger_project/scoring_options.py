from dataclasses import dataclass


@dataclass()
class ScoringOptions:
    similarity_weight: float = .5
    quality_weight: float = .5
    quality_metric_hardskill_weight: float = .6
    quality_metric_softskill_weight: float = .4