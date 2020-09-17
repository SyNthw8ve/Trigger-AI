import numpy
import tensorflow as tf
import pickle

from typing import List
from sentence_transformers import SentenceTransformer
from trigger.models.opening import Opening
from trigger.train.transformers.input_transformer import SentenceEmbedder

class OpeningInstance:

    def __init__(self, opening: Opening, sentenceEmbedder: SentenceEmbedder):

        self.opening = opening
        self.embedding = self._transformOpening(sentenceEmbedder)
        self.cluster_index = None

    def _transformOpening(self, sentenceEmbedder: SentenceEmbedder) -> numpy.array:

        hardSkillsSentence = ' '.join([hardSkill.name for hardSkill in self.opening.hardSkills])
        hardSkillsEmbedding = sentenceEmbedder.generateEmbeddings(hardSkillsSentence)

        softSkillsSentence = ' '.join([softSkill.name for softSkill in self.opening.softSkills])
        softSkillsEmbedding = sentenceEmbedder.generateEmbeddings(softSkillsSentence)

        averageEmbedding = tf.keras.layers.Average()([hardSkillsEmbedding, softSkillsEmbedding])

        return averageEmbedding.numpy()

    @staticmethod
    def save_instances(filename, instances: List["OpeningInstance"]) -> None:

        with open(filename, 'wb') as file:

            pickle.dump(instances, file)

    @staticmethod
    def load_instances(filename) -> List["OpeningInstance"]:

        openings_instances = []

        with open(filename, 'rb') as file:

            openings_instances = pickle.load(file)

        return openings_instances