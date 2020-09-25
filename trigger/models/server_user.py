from typing import NamedTuple, List

from attr import dataclass

from trigger.models.softskill import Softskill
from trigger.models.hardskill import Hardskill
from trigger.models.user import User


@dataclass(frozen=True)
class ServerUser(User):
    id: str