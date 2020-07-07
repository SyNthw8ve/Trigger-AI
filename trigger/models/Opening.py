from typing import NamedTuple, List

from trigger.models.Softskill import Softskill
from trigger.models.Hardskill import Hardskill
from trigger.models.Language import Language


class Opening(NamedTuple):
    # Institution's sector, really
    sector: str
    area: str
    languages: List[Language]
    hardSkills: List[Hardskill]
    softSkills: List[Softskill]
