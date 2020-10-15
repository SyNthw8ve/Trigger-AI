import pickle
from typing import Optional, List

from dataclasses import dataclass
from enum import Enum, unique

from trigger.train.transformers.opening_transformer import OpeningInstance


@unique
class OperationType(Enum):
    NEW_OPENING = 0
    UPDATE_OPENING = 1
    REMOVE_OPENING = 2


@dataclass(frozen=True)
class Operation:
    type: OperationType
    opening_instance_tag: Optional[str] = None
    opening_instance: Optional[OpeningInstance] = None


def read_operations(path: str) -> List[Operation]:
    with open(path, 'rb') as file:
        return pickle.load(file)
