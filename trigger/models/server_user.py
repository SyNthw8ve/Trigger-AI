from trigger.models.hardskill import Hardskill
from typing import List
from trigger.models.softskill import Softskill
from trigger.models.user import User


class ServerUser(User):

    def __init__(self, name: str, softSkills: List[Softskill], hardSkills: List[Hardskill], id: str) -> None:
        super().__init__(name, softSkills, hardSkills)
        self.id = id
