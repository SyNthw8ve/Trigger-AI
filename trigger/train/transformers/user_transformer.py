import tensorflow as tf
import numpy
import pickle

from typing import List
from trigger.models.user import User
from trigger.train.transformers.input_transformer import SentenceEmbedder

class UserInstance:

    def __init__(self, user: User, sentenceEmbedder: SentenceEmbedder):

        self.user = user
        self.embedding = self._transformUser(sentenceEmbedder)

    def _transformUser(self, sentenceEmbedder: SentenceEmbedder) -> numpy.array:

        hardSkillsSentence = ' '.join([hardSkill.name for hardSkill in self.user.hardSkills])
        hardSkillsEmbedding = sentenceEmbedder.generateEmbeddings(hardSkillsSentence)

        softSkillsSentence = ' '.join([softSkill.name for softSkill in self.user.softSkills])
        softSkillsEmbedding = sentenceEmbedder.generateEmbeddings(softSkillsSentence)

        averageEmbedding = tf.keras.layers.Average()([hardSkillsEmbedding, softSkillsEmbedding])

        return averageEmbedding.numpy()

    @staticmethod
    def save_instances(filename, instances: List["UserInstance"]) -> None:

        with open(filename, 'wb') as file:

            pickle.dump(instances, file)

    @staticmethod
    def load_instances(filename) -> List["UserInstance"]:

        users_instances = []

        with open(filename, 'rb') as file:

            users_instances = pickle.load(file)

        return users_instances