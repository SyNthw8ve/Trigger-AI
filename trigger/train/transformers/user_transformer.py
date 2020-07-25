import tensorflow as tf
import numpy

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