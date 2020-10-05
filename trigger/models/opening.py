from typing import NamedTuple, List

from dataclasses import dataclass

from trigger.models.softskill import Softskill
from trigger.models.hardskill import Hardskill
from trigger.models.language import Language

@dataclass(frozen=True)
class Opening:
    entityId: str
    hardSkills: List[Hardskill]
    softSkills: List[Softskill]
