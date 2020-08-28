from typing import Any, Dict, List, Optional
from util.stream.processor import Processor
from scipy.spatial.distance import cdist, seuclidean

from sklearn.cluster import Birch as SBirch

import math

import numpy as np

import time


class Cluster:
    def __init__(self, center: Any, index: int) -> None:
        self.center = center
        self.radius = 0
        self.instances = [center]
        self.index = index


class Birch(Processor):

    def __init__(self, threshold: float = 0.5, branching_factor: int = 50, compute_labels=True, copy=True) -> None:
        self.model = SBirch(
            threshold=threshold,
            branching_factor=branching_factor,
            compute_labels=compute_labels,
            n_clusters=None,
            copy=copy
        )
        self.instances = []

    def offline(self) -> None:
        self.model.partial_fit()

    def process(self, instance: Any) -> None:
        return self.add(instance)

    def add(self, instance: Any) -> None:
        self.model.partial_fit(np.array([instance]))
        self.instances.append(instance)

    def index_of_cluster_containing(self, instance: Any) -> Optional[int]:
        return self.model.predict(np.array([instance]))[0]

    def describe(self) -> Dict[str, Any]:
        '''
        This describes this clustering algortihm's parameters
        '''

        return {
            "name": "Birch",
            "parameters": self.model.get_params(True)
        }

    # def _predict(self, instance: UserInstance) -> int:

    #     clusterIndex = self.cluster.predict([instance.embedding])

    #     return clusterIndex[0]

    # def _computeScore(self, userInstance: UserInstance, openingInstance: OpeningInstance) -> float:

    #     return 1 - cosine(userInstance.embedding, openingInstance.embedding)

    # def getOpenings(self, instance: UserInstance) -> List[Match]:

    #     clusterIndex = self._predict(instance)

    #     openingsOfInterest = [
    #         openingInstance for openingInstance in self.instances if openingInstance.cluster_index == clusterIndex]

    #     return [Match(instance.user, self._computeScore(instance, openingInstance), openingInstance.opening) for openingInstance in openingsOfInterest]
