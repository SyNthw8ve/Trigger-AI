from typing import Any, Dict, List, Optional
from util.stream.processor import Processor
from scipy.spatial.distance import cdist, seuclidean

import math

from util.stream.processor import Processor
import time

class Cluster:
    def __init__(self, center: Any, index: int) -> None:
        self.center = center
        self.radius = 0
        self.instances = [center]
        self.index = index


class ECM(Processor):

    def __init__(self, distance_threshold: float, d) -> None:
        self.clusters: List[Cluster] = []
        self.distance_threshold = distance_threshold
        self.did_first_add = False
        self.instance_to_cluster: Dict[Any, int] = {}

    def process(self, instance: Any) -> None:
        return self.add(instance)

    def add(self, instance: Any) -> None:
        if not self.did_first_add:
            cluster = Cluster(instance, len(self.clusters))
            self.clusters.append(cluster)
            cluster.instances.append(instance)
            self.instance_to_cluster[tuple(instance)] = cluster.index

            self.did_first_add = True

            self.min_t = 0
            self.centers_t = 0
            self.shape_t = 0
            self.distances_t = 0
            self.radiuses_t = 0
            self.diffs_t = 0
            self.possible_t = 0

            return

        tic = time.perf_counter()

        centers = [cluster.center for cluster in self.clusters]

        toc = time.perf_counter()
        self.centers_t += toc - tic

        tic = time.perf_counter()

        distances = cdist(
            np.array([instance]),
            np.array(centers),
            'euclidean'
        )[0]

        toc = time.perf_counter()
        self.distances_t += toc - tic

        tic = time.perf_counter()

        radiuses = [cluster.radius for cluster in self.clusters]

        toc = time.perf_counter()
        self.radiuses_t += toc - tic

        tic = time.perf_counter()

        diffs = distances - radiuses

        toc = time.perf_counter()
        self.diffs_t += toc - tic

        tic = time.perf_counter()

        possible = np.where(diffs <= 0)[0]

        toc = time.perf_counter()
        self.possible_t += toc - tic

        tic = time.perf_counter()

        min_index = None if possible.size == 0 else distances.argmin()

        # print("I", instance, "Ds", distances, "Cs", centers, "Rs", radiuses, "min_index", min_index)

        toc = time.perf_counter()

        self.min_t += toc - tic

        if min_index is not None:
            self.clusters[min_index].instances.append(instance)
            self.instance_to_cluster[tuple(instance)] = min_index

            return

        distances_plus_radiuses = np.add(distances, radiuses)
        lowest_distance_and_radius_index = np.argmin(
            distances_plus_radiuses)
        lowest_distance_and_radius = distances_plus_radiuses[lowest_distance_and_radius_index]

        if lowest_distance_and_radius > 2 * self.distance_threshold:
            cluster = Cluster(instance, len(self.clusters))
            self.clusters.append(cluster)
            self.instance_to_cluster[tuple(instance)] = cluster.index

        else:
            cluster = self.clusters[lowest_distance_and_radius_index]
            direction = instance - cluster.center

            cluster.radius = lowest_distance_and_radius/2

            cluster.center = instance - (
                direction / np.linalg.norm(direction)) * cluster.radius

            cluster.instances.append(instance)
            self.instance_to_cluster[tuple(instance)] = cluster.index

            self.instances.append(instance)

    def index_of_cluster_containing(self, instance: Any) -> Optional[int]:
        return self.instance_to_cluster[tuple(instance)]

    def describe(self) -> Dict[str, Any]:
        '''
        This describes this clustering algortihm's parameters
        '''

        return {
            "name": "ECM",
            "parameters": {
                "distance threshold": self.distance_threshold
            }
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
