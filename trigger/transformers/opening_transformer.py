from typing import Iterable, List, Tuple
from trigger.transformers.input_transformer import SentenceEmbedder
from trigger.instances.opening_instance import OpeningInstance
from interference.transformers.transformer_pipeline import TransformerPipeline, Instance

from typing_extensions import Literal, Final

import numpy
import tensorflow as tf

from ..models.opening import Opening

LAYER = Literal['avg', 'concat', 'no_ss']

class OpeningTransformer(TransformerPipeline[Opening]):

    def __init__(self, sentenceEmbedder: SentenceEmbedder = SentenceEmbedder(), layer: LAYER = 'avg', normed:bool = False):
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


def transform_openings_using_layers(
    openings: List[Opening],
    layers: List[LAYER] = ['avg', 'concat', 'no_ss'],
    normed_options: List[bool] = [True, False]
) -> Iterable[Tuple[LAYER, bool, List[OpeningInstance]]]:
    
    for layer in layers:
        for normed_option in normed_options:
            transformer = OpeningTransformer(layer=layer, normed=normed_option)

            yield layer, normed_option, [
                transformer.transform(opening)
                for opening in openings
            ]