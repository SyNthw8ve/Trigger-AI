from typing import List
import pickle
import numpy
from ..models.opening import Opening


class OpeningInstance:

    def __init__(self, opening: Opening, embedding: numpy.array):
        self.opening = opening
        self.embedding = embedding

    @staticmethod
    def save_instances(filename: str, instances: List["OpeningInstance"]) -> None:

        with open(filename, 'wb') as file:

            pickle.dump(instances, file)

    @staticmethod
    def load_instances(filename: str) -> List["OpeningInstance"]:

        with open(filename, 'rb') as file:

            openings_instances: List["OpeningInstance"] = pickle.load(file)
            return openings_instances