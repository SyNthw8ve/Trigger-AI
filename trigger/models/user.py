from typing import List

from dataclasses import dataclass

from .softskill import Softskill
from .hardskill import Hardskill


@dataclass(frozen=True)
class User:
    name: str
    softSkills: List[Softskill]
    hardSkills: List[Hardskill]
