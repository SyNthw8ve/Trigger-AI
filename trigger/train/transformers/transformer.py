from abc import ABC, abstractmethod
from typing import Generic, Type, TypeVar

import numpy

T = TypeVar('T')
I = TypeVar('I')

class Transformer(ABC, Generic[T, I]):

    @abstractmethod
    def calculate_embedding(self, value: T) -> numpy.ndarray:
        pass

    @abstractmethod
    def transform_to_instance(self, value: T) -> I:
        pass