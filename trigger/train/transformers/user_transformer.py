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

        hardSkillsEmbedding = sentenceEmbedder.generateEmbeddingsFromList(self.user.hardSkills)

        softSkillsEmbedding = sentenceEmbedder.generateEmbeddingsFromList(self.user.softSkills)

        averageEmbedding = tf.keras.layers.Average()([hardSkillsEmbedding, softSkillsEmbedding])
        #averageEmbedding = tf.keras.layers.concatenate([hardSkillsEmbedding, softSkillsEmbedding])

        resultingEmbedding = averageEmbedding.numpy()
        resultingEmbedding = resultingEmbedding / numpy.linalg.norm(resultingEmbedding)

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