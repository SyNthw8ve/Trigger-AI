from typing import NamedTuple, List

from trigger.models.softskill import Softskill
from trigger.models.hardskill import Hardskill
from trigger.models.language import Language


class Opening(NamedTuple):
    # Institution's sector, really
    sector: str
    # Can this even be used?
    area: str
    languages: List[Language]
    hardSkills: List[Hardskill]
    softSkills: List[Softskill]
