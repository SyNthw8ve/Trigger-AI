from typing import NamedTuple, List

from trigger.models.softskill import Softskill
from trigger.models.hardskill import Hardskill


class User(NamedTuple):
    name: str
    softSkills: List[Softskill]
    # is this "competências"?...
    hardSkills: List[Hardskill]
    # Can this even be used?
    interests: List[str]
