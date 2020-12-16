from ..instances.opening_instance import OpeningInstance

from typing import List

from dataclasses import dataclass

@dataclass()
class Project:
    name: str
    openings: List[OpeningInstance]
