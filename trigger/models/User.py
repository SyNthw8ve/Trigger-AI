from typing import NamedTuple, List

from trigger.models.Softskill import Softskill


class User(NamedTuple):
    softSkills: List[Softskill]
