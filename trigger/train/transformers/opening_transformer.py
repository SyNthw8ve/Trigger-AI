import numpy
import tensorflow as tf
import pickle

from typing import List
from sentence_transformers import SentenceTransformer
from trigger.models.opening import Opening
from trigger.train.transformers.input_transformer import SentenceEmbedder

class OpeningInstance:

    def __init__(self, opening: Opening, sentenceEmbedder: SentenceEmbedder, layer:str='avg'):

        self.opening = opening
        self.embedding = self._transformOpening(sentenceEmbedder, layer)
        self.cluster_index = None

    def _transformOpening(self, sentenceEmbedder: SentenceEmbedder, layer) -> numpy.array:

        hardSkillsEmbedding = sentenceEmbedder.generateEmbeddingsFromList(self.opening.hardSkills)

        softSkillsEmbedding = sentenceEmbedder.generateEmbeddingsFromList(self.opening.softSkills)

        if layer == 'avg':

            concat_layer = tf.keras.layers.Average()([hardSkillsEmbedding, softSkillsEmbedding])

        elif layer == 'concat':

            concat_layer = tf.keras.layers.concatenate([hardSkillsEmbedding, softSkillsEmbedding])

        resultingEmbedding = concat_layer.numpy()
        #resultingEmbedding = resultingEmbedding / numpy.linalg.norm(resultingEmbedding)

        return resultingEmbedding

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