import tensorflow as tf
import numpy
import pickle

from typing import List
from trigger.models.user import User

from trigger.train.transformers.input_transformer import SentenceEmbedder

class UserInstance:

    def __init__(self, user: User, sentenceEmbedder: SentenceEmbedder, layer:str='avg', normed=False):

        self.user = user
        self.embedding = self._transformUser(sentenceEmbedder, layer, normed)

    def _transformUser(self, sentenceEmbedder: SentenceEmbedder, layer, normed) -> numpy.array:

        hardSkillsEmbedding = sentenceEmbedder.generateEmbeddingsFromList(self.user.hardSkills)

        softSkillsEmbedding = sentenceEmbedder.generateEmbeddingsFromList(self.user.softSkills)

        if layer == 'avg':
            jointEmbedding = tf.keras.layers.Average()([hardSkillsEmbedding, softSkillsEmbedding])

        elif layer == 'concat':
            jointEmbedding = tf.keras.layers.concatenate([hardSkillsEmbedding, softSkillsEmbedding])

        elif layer == 'no_ss':
            jointEmbedding = hardSkillsEmbedding

        if layer == 'no_ss':
            resultingEmbedding = jointEmbedding
            
        else:
            resultingEmbedding = jointEmbedding.numpy()

        if normed and not numpy.isnan(resultingEmbedding).any():

            resultingEmbedding = resultingEmbedding / numpy.linalg.norm(resultingEmbedding)

        return resultingEmbedding


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