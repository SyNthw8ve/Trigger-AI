from trigger_project.transformers.input_transformer import SentenceEmbedder
from trigger_project.instances.opening_instance import OpeningInstance
from interference.transformers.transformer_pipeline import TransformerPipeline, Instance

from typing_extensions import Literal, Final

import numpy
import tensorflow as tf

from ..models.opening import Opening

LAYER = Literal['avg', 'concat', 'no_ss']

class OpeningTransformer(TransformerPipeline[Opening]):

    def __init__(self, sentenceEmbedder: SentenceEmbedder = SentenceEmbedder(), layer: LAYER = 'avg', normed=False):
        self.sentenceEmbedder = sentenceEmbedder
        self.layer: Final[LAYER] = layer
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