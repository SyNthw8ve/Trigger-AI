from pathlib import Path
from typing import List
import pickle
from ..models.opening import Opening

from interference.transformers.transformer_pipeline import Instance

OpeningInstance = Instance[Opening]

class OpeningInstanceHelper:

    @staticmethod
    def save_instances(filename: str, instances: List["OpeningInstance"]) -> None:
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filename, 'wb') as file:
            pickle.dump(instances, file)

    @staticmethod
    def load_instances(filename: str) -> List["OpeningInstance"]:

        with open(filename, 'rb') as file:

            openings_instances: List["OpeningInstance"] = pickle.load(file)
            return openings_instances