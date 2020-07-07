from typing import NamedTuple, List

from trigger.models.Softskill import Softskill
from trigger.models.Hardskill import Hardskill


class User(NamedTuple):
    softSkills: List[Softskill]
    # is this "competências"?...
    hardSkills: List[Hardskill]
    interests: List[str]
