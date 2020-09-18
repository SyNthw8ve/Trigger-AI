import random
import pickle as pk
import numpy as np

from abc import ABC, abstractmethod
from typing import List

class StreamGenerator(ABC):

    @abstractmethod
    def generate_stream(self, num_items: int) -> List:
        pass

    @abstractmethod
    def save_stream(self, path: str):
        pass

class StreamGeneratorRandomDelay(StreamGenerator):

    def __init__(self, stream_values_interval: float, max_delay: float, min_delay: float, 
                    dimensions: int=2):

        self.stream_values_interval = stream_values_interval
        self.max_delay = max_delay
        self.min_delay = min_delay
        self.stream = []
        self.dimensions = dimensions

    def generate_stream(self, num_items: int) -> List:

        stream = []

        max_distance = self.stream_values_interval

        for i in range(num_items):

            vector = np.random.uniform(low=-max_distance, high=max_distance, size=self.dimensions).astype('float32')
            delay = random.uniform(self.min_delay, self.max_delay)

            stream.append((vector, delay))

        self.stream = stream

        return stream

    def save_stream(self, path: str):

        with open(path, 'wb') as f:
            pk.dump(self.stream, f)

class StreamGeneratorUniformDelay(StreamGenerator):

    def __init__(self, delay: float, stream_values_interval: float, dimensions: int=2):

        self.delay = delay
        self.dimensions = dimensions
        self.stream_values_interval = stream_values_interval
        self.stream = []

    def generate_stream(self, num_items: int) -> List:

        stream = []

        max_distance = self.stream_values_interval

        for i in range(num_items):

            vector = np.random.uniform(low=-max_distance, high=max_distance, size=self.dimensions).astype('float32')
            stream.append((vector, self.delay))

        self.stream = stream

        return stream

    def save_stream(self, path: str):

        with open(path, 'wb') as f:
            pk.dump(self.stream, f)

        