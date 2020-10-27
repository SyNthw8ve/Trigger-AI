from typing import List

from dataclasses import dataclass

from trigger.train.transformers.opening_transformer import OpeningInstance

@dataclass()
class Project:
    openings: List[OpeningInstance]