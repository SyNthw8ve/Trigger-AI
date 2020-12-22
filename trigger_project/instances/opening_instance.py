from typing import List
import pickle
from ..models.opening import Opening

from trigger.transformers.transformer_pipeline import Instance


class OpeningInstance(Instance[Opening]):

    @staticmethod
    def save_instances(filename: str, instances: List["OpeningInstance"]) -> None:

        with open(filename, 'wb') as file:

            pickle.dump(instances, file)

    @staticmethod
    def load_instances(filename: str) -> List["OpeningInstance"]:

        with open(filename, 'rb') as file:

            openings_instances: List["OpeningInstance"] = pickle.load(file)
            return openings_instances