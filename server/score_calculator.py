from scipy.spatial.distance import cosine

from trigger.train.transformers.opening_transformer import OpeningInstance
from trigger.train.transformers.user_transformer import UserInstance
from abc import ABC, abstractmethod


class ScoreCalculator(ABC):


    @abstractmethod
    def calculate(self,
                  user_instance: UserInstance,
                  opening_instance: OpeningInstance) -> float:
        pass


class SimilarityScoreCalculator(ScoreCalculator):


    def calculate(self,
                  user_instance: UserInstance,
                  opening_instance: OpeningInstance) -> float:
        return 1 - cosine(user_instance.embedding, opening_instance.embedding)


class QualityScoreCalculator(ScoreCalculator):

    def __init__(self, weight_hs=0.5, weight_ss=0.5):
        self.weight_ss = weight_ss
        self.weight_hs = weight_hs

    def calculate(self,
                  user_instance: UserInstance,
                  opening_instance: OpeningInstance) -> float:
        user = user_instance.user
        opening = opening_instance.opening

        user_ss_set = set([ss.name for ss in user.softSkills])
        opening_ss_set = set([ss.name for ss in opening.softSkills])

        ss_score = len(user_ss_set.intersection(opening_ss_set))/len(opening_ss_set)


        user_hs_set = set([hs.name for hs in user.hardSkills])
        opening_hs_set = set([hs.name for hs in opening.hardSkills])
        hs_score = len(user_hs_set.intersection(opening_hs_set)) / len(opening_hs_set)


        return self.weight_ss * ss_score + self.weight_hs * hs_score

class RealScoreCalculator(ScoreCalculator):

    def __init__(self, weight_similarity=0.5, weight_quality=0.5):
        self.weight_quality = weight_quality
        self.weight_similarity = weight_similarity
        self.quality_score_calculator = QualityScoreCalculator()
        self.similarity_score_calculator = SimilarityScoreCalculator()

    def calculate(self,
                  user_instance: UserInstance,
                  opening_instance: OpeningInstance) -> float:
        return self.weight_quality * self.quality_score_calculator.calculate(user_instance, opening_instance) \
               + self.weight_similarity * self.similarity_score_calculator.calculate(user_instance, opening_instance)

