from typing import NamedTuple, List

from dataclasses import dataclass

from .softskill import Softskill
from .hardskill import Hardskill

@dataclass()
class Opening:
    entityId: str
    hardSkills: List[Hardskill]
    softSkills: List[Softskill]
