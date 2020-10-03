from typing import Any, Dict, List, Optional, Tuple
from util.stream.processor import Processor
from scipy.spatial.distance import cdist, seuclidean

import numpy as np

from enum import Enum

class Cluster:
    def __init__(self, center: Any, index: int) -> None:
        self.center = center
        self.radius = 0
        self.instances = [center]
        self.index = index


class SearchResultType(Enum):
    RADIUS = 1
    THRESHOLD = 2
    OUTSIDE = 3


class ECM(Processor):

    def __init__(self, distance_threshold: float) -> None:
        self.clusters: List[Cluster] = []
        self.distance_threshold = distance_threshold
        self.did_first_add = False
        self.instance_to_cluster: Dict[Any, int] = {}

    
    @property
    def instances(self):
        return list(self.instance_to_cluster.keys())

    def online_fase(self, instance: Any) -> None:
        return self.add(instance)

    def process(self, instance: Any) -> None:
        return self.add(instance)

    def add(self, instance: Any) -> None:
        if not self.did_first_add:
            cluster = Cluster(instance, len(self.clusters))
            self.clusters.append(cluster)
            cluster.instances.append(instance)
            self.instance_to_cluster[tuple(instance)] = cluster.index

            self.did_first_add = True
            return

        search_result, (index, distance) = self._search_index_and_distance(instance)

        if search_result == SearchResultType.RADIUS:
            self.clusters[index].instances.append(instance)
            self.instance_to_cluster[tuple(instance)] = index

        elif search_result == SearchResultType.THRESHOLD:
            cluster = self.clusters[index]
            direction = instance - cluster.center

            cluster.radius = distance / 2

            cluster.center = instance - (direction / np.linalg.norm(direction)) * cluster.radius

            cluster.instances.append(instance)
            self.instance_to_cluster[tuple(instance)] = cluster.index

        elif search_result == SearchResultType.OUTSIDE:
            cluster = Cluster(instance, len(self.clusters))
            self.clusters.append(cluster)
            self.instance_to_cluster[tuple(instance)] = cluster.index


    def _search_index_and_distance(self, instance: Any) -> \
            Tuple[SearchResultType, Tuple[Optional[int], Optional[int]]]:

        centers = [cluster.center for cluster in self.clusters]

        distances = cdist(
            np.array([instance]),
            np.array(centers),
            'euclidean'
        )[0]

        radiuses = [cluster.radius for cluster in self.clusters]

        diffs = distances - radiuses

        possible = np.where(diffs <= 0)[0]

        min_index = None if possible.size == 0 else distances.argmin()

        if min_index is not None:
            return SearchResultType.RADIUS, (min_index, distances[min_index])

        distances_plus_radiuses = np.add(distances, radiuses)
        lowest_distance_and_radius_index = np.argmin(distances_plus_radiuses)
        lowest_distance_and_radius = distances_plus_radiuses[lowest_distance_and_radius_index]

        if lowest_distance_and_radius > 2 * self.distance_threshold:
            return SearchResultType.OUTSIDE, (None, None)

        else:
            return SearchResultType.THRESHOLD, (lowest_distance_and_radius_index, lowest_distance_and_radius)
    

    def index_of_cluster_containing(self, instance: Any) -> Optional[int]:
        return self.instance_to_cluster[tuple(instance)]

    def get_cluster(self, instance: Any) -> Optional[int]:
        return self.index_of_cluster_containing(instance)

    def describe(self) -> Dict[str, Any]:
        """
        This describes this clustering algorithm's parameters
        """

        return {
            "name": "ECM",
            "parameters": {
                "distance threshold": self.distance_threshold
            }
        }

    def safe_file_name(self) -> str:
        return f"ECM = distance_threshold={self.distance_threshold}"

    def predict(self, instance: Any) -> Optional[int]:

        if self.did_first_add:
            return None

        search_result, (index, distance) = self._search_index_and_distance(instance)
        if search_result == SearchResultType.OUTSIDE:
            return None

        elif search_result == SearchResultType.THRESHOLD:
            return index

        elif search_result == SearchResultType.RADIUS:
            return index

    # def _computeScore(self, userInstance: UserInstance, openingInstance: OpeningInstance) -> float:

    #     return 1 - cosine(userInstance.embedding, openingInstance.embedding)

    # def getOpenings(self, instance: UserInstance) -> List[Match]:

    #     clusterIndex = self._predict(instance)

    #     openingsOfInterest = [
    #         openingInstance for openingInstance in self.instances if openingInstance.cluster_index == clusterIndex]

    #     return [Match(instance.user, self._computeScore(instance, openingInstance), openingInstance.opening) for openingInstance in openingsOfInterest]
