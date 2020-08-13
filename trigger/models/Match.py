from typing import NamedTuple

from trigger.models.user import User
from trigger.models.opening import Opening


class Match(NamedTuple):
    user: User
    score: float
    opening: Opening
