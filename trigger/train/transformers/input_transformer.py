from typing import List, Any
from sentence_transformers import SentenceTransformer
import tensorflow as tf
import numpy

class SentenceEmbedder:

    def __init__(self, modelname:str='roberta-large-nli-stsb-mean-tokens'):

        self.model = SentenceTransformer(modelname)

    def generateEmbeddings(self, sentence: str) -> numpy.array:

        return self.model.encode(sentence)

    def generateEmbeddingsFromList(self, skill_list: List[Any]) -> numpy.array:

        skills_embedding = []

        for skill in skill_list:

            skills_embedding.append(self.model.encode(skill.name))

        if len(skill_list) == 0:

            return numpy.zeros(1024)

        elif len(skill_list) == 1:

            return skills_embedding[0]

        else:

            return tf.keras.layers.Average()(skills_embedding).numpy()