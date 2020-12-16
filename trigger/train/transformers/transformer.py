from abc import ABC, abstractmethod
from typing import Generic, TypeVar

import numpy

T = TypeVar('T')

class Transformer(ABC, Generic[T]):

    def for_class() -> T:
        return T

    @abstractmethod
    def transform(self, value: T) -> numpy.array:
        pass