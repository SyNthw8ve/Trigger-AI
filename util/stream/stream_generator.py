import random
import pickle as pk

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

    def __init__(self, stream_values_interval: float, max_delay: float, min_delay: float):

        self.stream_values_interval = stream_values_interval
        self.max_delay = max_delay
        self.min_delay = min_delay
        self.stream = []

    def generate_stream(self, num_items: int) -> List:

        stream = []

        max_distance = self.stream_values_interval

        for i in range(num_items):

            x = random.uniform(-max_distance, max_distance)
            y = random.uniform(-max_distance, max_distance)
            delay = random.uniform(self.min_delay, self.max_delay)

            stream.append((x, y, delay))

        self.stream = stream

        return stream

    def save_stream(self, path: str):

        with open(path, 'wb') as f:
            pk.dump(self.stream, f)

class StreamGeneratorUniformDelay(StreamGenerator):

    def __init__(self, delay: float, stream_values_interval: float):

        self.delay = delay
        self.stream_values_interval = stream_values_interval
        self.stream = []

    def generate_stream(self, num_items: int) -> List:

        stream = []

        max_distance = self.stream_values_interval

        for i in range(num_items):

            x = random.uniform(-max_distance, max_distance)
            y = random.uniform(-max_distance, max_distance)

            stream.append((x, y, self.delay))

        self.stream = stream

        return stream

    def save_stream(self, path: str):

        with open(path, 'wb') as f:
            pk.dump(self.stream, f)

        