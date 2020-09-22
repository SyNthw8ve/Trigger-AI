from typing import NamedTuple, List

from trigger.models.softskill import Softskill
from trigger.models.hardskill import Hardskill


class User(NamedTuple):
    name: str
    softSkills: List[Softskill]
    hardSkills: List[Hardskill]
