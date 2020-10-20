from typing import List

from dataclasses import dataclass

from trigger.models.softskill import Softskill
from trigger.models.hardskill import Hardskill


@dataclass()
class Opening:
    entityId: str
    hardSkills: List[Hardskill]
    softSkills: List[Softskill]
