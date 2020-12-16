from trigger.train.transformers.sentence_embedder import SentenceEmbedder
from trigger.train.transformers.transformer import Transformer

import numpy
import tensorflow as tf

from ..models.opening import Opening

class OpeningTransformer(Transformer[Opening]):

    def __init__(self, sentenceEmbedder: SentenceEmbedder, layer:str='avg', normed=False):
        self.sentenceEmbedder = sentenceEmbedder
        self.layer = layer
        self.normed = normed

    def transform(self, opening: Opening) -> numpy.array:

        hardSkillsEmbedding = self.sentenceEmbedder.generateEmbeddingsFromList(opening.hardSkills)

        softSkillsEmbedding = self.sentenceEmbedder.generateEmbeddingsFromList(opening.softSkills)

        if self.layer == 'avg':
            jointEmbedding = tf.keras.layers.Average()([hardSkillsEmbedding, softSkillsEmbedding])

        elif self.layer == 'concat':
            jointEmbedding = tf.keras.layers.concatenate([hardSkillsEmbedding, softSkillsEmbedding])

        elif self.layer == 'no_ss':
            jointEmbedding = hardSkillsEmbedding

        if self.layer == 'no_ss':
            resultingEmbedding = jointEmbedding
            
        else:
            resultingEmbedding = jointEmbedding.numpy()

        if self.normed and not numpy.isnan(resultingEmbedding).any():

            resultingEmbedding = resultingEmbedding / numpy.linalg.norm(resultingEmbedding)

        return resultingEmbedding