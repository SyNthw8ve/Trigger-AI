from trigger_project.transformers.input_transformer import SentenceEmbedder
from trigger_project.instances.opening_instance import OpeningInstance
from trigger.transformers.transformer_pipeline import TransformerPipeline, Instance

import numpy
import tensorflow as tf

from ..models.opening import Opening

class OpeningTransformer(TransformerPipeline[Opening]):

    def __init__(self, sentenceEmbedder: SentenceEmbedder = SentenceEmbedder(), layer: str = 'avg', normed=False):
        self.sentenceEmbedder = sentenceEmbedder
        self.layer = layer
        self.normed = normed

    def calculate_embedding(self, opening: Opening) -> numpy.ndarray:
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

    def transform(self, opening: Opening) -> OpeningInstance:
        embedding = self.calculate_embedding(opening)
        return OpeningInstance(opening, embedding)