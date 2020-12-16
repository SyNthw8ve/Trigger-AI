from trigger.match import Match
from .user import User
from .opening import Opening
from dataclasses import dataclass

@dataclass()
class TriggerMatch(Match):
    user: User
    opening: Opening