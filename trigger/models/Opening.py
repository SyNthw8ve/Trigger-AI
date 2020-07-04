from typing import NamedTuple, List

from trigger.models.SoftSkill import SoftSkill


class Opening(NamedTuple):
    softSkills: List[SoftSkill]
    value: float
