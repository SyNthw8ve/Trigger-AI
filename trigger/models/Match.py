from typing import NamedTuple

from trigger.models.User import User
from trigger.models.Opening import Opening


class Match(NamedTuple):
    user: User
    score: float
    opening: Opening
