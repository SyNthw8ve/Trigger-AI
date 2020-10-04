from abc import ABC, abstractmethod
from typing import Any, Tuple, List, Optional

import numpy


class Clusterer(ABC):

    @abstractmethod
    def process(self, tag: str, instance: numpy.array, custom_data: Any=None) -> None:
        pass

    @abstractmethod
    def update(self, tag: str, instance: numpy.array, custom_data: Any=None) -> None:
        pass

    @abstractmethod
    def remove(self, tag: str) -> None:
        pass

    @abstractmethod
    def get_cluster(self, instance: numpy.array) -> Optional[int]:
        pass

    @abstractmethod
    def get_cluster_by_tag(self, tag: str) -> Optional[int]:
        pass

    @abstractmethod
    def get_instances_and_tags_in_cluster(self, cluster_id: int) -> Tuple[List[numpy.array], List[str]]:
        pass

    # TODO: It's debatable if this is needed.
    # Mainly for Debugging?
    @abstractmethod
    def get_all_instances_with_tags(self) -> Tuple[List[Any], List[str]]:
        pass

    @abstractmethod
    def get_instance_with_tag(self, tag: str) -> Optional[Any]:
        pass

    @abstractmethod
    def predict(self, instance) -> int:
        pass

