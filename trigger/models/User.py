from typing import NamedTuple, List

from trigger.models.SoftSkill import SoftSkill


class User(NamedTuple):
    softSkills: List[SoftSkill]
