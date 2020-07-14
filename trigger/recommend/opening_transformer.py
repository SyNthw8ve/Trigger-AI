import numpy

from trigger.models.opening import Opening
from trigger.recommend.skill_transformers.soft_skill_transformer import SoftskillTransformer

OpeningPoint = numpy.array


class OpeningTransformer:
    def __init__(self, softskill_transformer: SoftskillTransformer):
        self.softskill_transformer = softskill_transformer
        # Leadership
        # Creativity
        # Individuality

    def transform(self, opening: Opening) -> OpeningPoint:
        softskills_point = self.softskill_transformer.transform(opening.softSkills)
        return numpy.array(softskills_point)
