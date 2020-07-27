from typing import List, Dict

import numpy

from trigger.models.user import User
from trigger.recommend.skill_transformers.soft_skill_transformer import SoftskillTransformer

UserPoint = numpy.array


class UserTransformer:

    def __init__(self, softskill_transformer: SoftskillTransformer):
        self.softskill_transformer = softskill_transformer
        # Leadership
        # Creativity
        # Individuality

    def transform(self, user: User) -> UserPoint:
        softskills_point = self.softskill_transformer.transform(user.softSkills)
        return numpy.array(softskills_point)
