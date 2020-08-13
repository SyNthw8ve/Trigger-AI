from typing import List
from sentence_transformers import SentenceTransformer

import numpy

class SentenceEmbedder:

    def __init__(self, modelname:str='roberta-large-nli-stsb-mean-tokens'):

        self.model = SentenceTransformer(modelname)

    def generateEmbeddings(self, sentence: str) -> numpy.array:

        return self.model.encode(sentence)[0]