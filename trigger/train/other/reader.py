import json

from typing import List

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



