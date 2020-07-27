import json

from typing import List

from trigger.models.opening import Opening
from trigger.models.softskill import Softskill
from trigger.models.hardskill import Hardskill
from trigger.models.language import Language
from trigger.models.user import User

class SkillsFileReader:

    def __init__(self, filename: str):

        self.filename = filename
        self.hardskills = []
        self.softskills = []
        self.competences = []
        self.languages = []

        self._populate()

    def _populate(self):

        with open(self.filename, 'r') as file:

            skills = json.load(file)

            self.hardskills = skills.get('Hardskills', [])
            self.softskills = skills.get('Softskills', [])
            self.competences = skills.get('Competences', [])
            self.languages = skills.get('Languages', [])

class DataReaderUsers:

    def __init__(self, filename: str):

        self.filename = filename
        self.users = self.populate()

    def populate(self) -> List[User]:

        users = []

        state_starts = {0: "User:",
                        1: "Hardskills:",
                        2: "Softskills:"}

        with open(self.filename, 'r') as file:

            lines = file.readlines()
            state = 0
            username = ''
            hardskills = []
            softskills = []
            
            for line in lines:

                if state == 0 and line.startswith(state_starts[state]):

                    if username != '':

                        user_softskills = [Softskill(name=softskill, score=0) for softskill in softskills]
                        user_hardskills = [Hardskill(name=hardskill) for hardskill in hardskills]

                        user = User(name=username, hardSkills=user_hardskills, softSkills=user_softskills, interests=["Eating"])

                        username = ''
                        hardskills = []
                        softskills = []

                        users.append(user)

                    state = 1
                    username = line.split(":", 1)[1].strip()

                elif state == 1 and line.startswith(state_starts[state]):

                        state = 2
                        hardskills_temp = line.split(":", 1)[1].strip()
                        hardskills = [h_t.strip() for h_t in hardskills_temp.split(",") if h_t.strip() != '']

                elif state == 2 and line.startswith(state_starts[state]):

                        state = 0
                        softskills_temp = line.split(":", 1)[1].strip()
                        softskills = [s_t.strip() for s_t in softskills_temp.split(",") if s_t.strip() != '']

            if state == 0:

                user_softskills = [Softskill(name=softskill, score=0) for softskill in softskills]
                user_hardskills = [Hardskill(name=hardskill) for hardskill in hardskills]

                user = User(name=username, hardSkills=user_hardskills, softSkills=user_softskills, interests=["Eating"])

                users.append(user)
                        
                        
        return users

class DataReaderOpenings:

    def __init__(self, filename: str):

        self.filename = filename
        self.openings = self.populate()

    def populate(self) -> List[Opening]:

        openings = []

        state_starts = {0: "Sector:",
                        1: "Area:", 2: "Hardskills:",
                        3: "Softskills:"}

        with open(self.filename, 'r') as file:

            lines = file.readlines()
            state = 0
            sector = ''
            area = ''
            hardskills = []
            softskills = []

            for line in lines:

                if state == 0 and line.startswith(state_starts[state]):

                    if sector != '':
                        opening_softskills = [
                            Softskill(name=softskill, score=0) for softskill in softskills]

                        opening_hardskills = [
                            Hardskill(name=hardskill) for hardskill in hardskills]

                        opening = Opening(entityId=len(openings), sector=sector, area=area, hardSkills=opening_hardskills,
                                          softSkills=opening_softskills, languages=[Language(name="English")])

                        openings.append(opening)

                    area = ''
                    hardskills = []
                    softskills = []
                    sector = line.split(":", 1)[1].strip()

                    state = 1

                elif state == 1 and line.startswith(state_starts[state]):

                    state = 2
                    area = line.split(":", 1)[1].strip()

                elif state == 2 and line.startswith(state_starts[state]):

                    state = 3
                    hardskills_temp = line.split(":", 1)[1].strip()
                    hardskills = [h_t.strip() for h_t in hardskills_temp.split(",") if h_t.strip() != '']

                elif state == 3 and line.startswith(state_starts[state]):

                    state = 0
                    softskills_temp = line.split(":", 1)[1].strip()
                    softskills = [s_t.strip() for s_t in softskills_temp.split(",") if s_t.strip() != '']

            if state == 0:
                opening_softskills = [
                    Softskill(name=softskill, score=0) for softskill in softskills]

                opening_hardskills = [
                    Hardskill(name=hardskill) for hardskill in hardskills]

                opening = Opening(entityId=len(openings), sector=sector, area=area, hardSkills=opening_hardskills,
                                softSkills=opening_softskills, languages=[Language(name="English")])

                openings.append(opening)

        return openings