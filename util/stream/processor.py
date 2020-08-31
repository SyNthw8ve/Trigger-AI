from abc import ABC, abstractmethod

class Processor(ABC):

    @abstractmethod
    def process(self, instance):
        pass

    @abstractmethod
    def get_cluster(self, instance):
        pass