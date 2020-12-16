from trigger.train.transformers.transformer import Transformer
from trigger.train.transformers.sentence_embedder import SentenceEmbedder

import tensorflow as tf
import numpy

from ..models.user import User


class UserTransformer(Transformer[User]):

    def __init__(self, sentenceEmbedder: SentenceEmbedder, layer:str='avg', normed=False):
        self.sentenceEmbedder = sentenceEmbedder
        self.layer = layer
        self.normed = normed

    def transform(self, user: User) -> numpy.array:
        
        hardSkillsEmbedding = self.sentenceEmbedder.generateEmbeddingsFromList(user.hardSkills)

        softSkillsEmbedding = self.sentenceEmbedder.generateEmbeddingsFromList(user.softSkills)

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