from dataclasses import dataclass
from .models.opening import Opening


@dataclass()
class ScoringResult:
    opening: Opening
    similarity_score: float
    similarity_weight: float
    quality_score: float
    quality_weight: float
    final_score: float