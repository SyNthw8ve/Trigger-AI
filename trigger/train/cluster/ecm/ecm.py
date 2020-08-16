from typing import Any, List, Optional
from scipy.spatial.distance import euclidean

import numpy as np


class Cluster:
    def __init__(self, center: Any) -> None:
        self.center = center
        self.radius = 0
        self.instances = [center]


class ECM:

    def __init__(self, distance_threshold: float) -> None:
        self.clusters: List[Cluster] = []
        self.distance_threshold = distance_threshold
        self.did_first_add = False

    def add(self, instance: Any) -> None:
        if not self.did_first_add:
            self.clusters.append(Cluster(instance))
            self.did_first_add = True
        else:
            centers = [cluster.center for cluster in self.clusters]
            distances = [euclidean(center, instance) for center in centers]
            radiuses = [cluster.radius for cluster in self.clusters]

            # if D min is less than any cluster radius then
            min_value = 999999999
            min_index = None
            for index, (distance, radius) in enumerate(zip(distances, radiuses)):
                if distance <= radius and distance < min_value:
                    min_index = index
                    min_value = distance

            if min_index is not None:
                self.clusters[min_index].instances.append(instance)
            else:
                distances_plus_radiuses = np.add(distances, radiuses)
                lowest_distance_and_radius_index = np.argmin(
                    distances_plus_radiuses)
                lowest_distance_and_radius = distances_plus_radiuses[lowest_distance_and_radius_index]
                if lowest_distance_and_radius > 2 * self.distance_threshold:
                    self.clusters.append(Cluster(instance))
                else:
                    cluster = self.clusters[lowest_distance_and_radius_index]
                    direction = instance - cluster.center

                    cluster.radius = lowest_distance_and_radius/2

                    cluster.center = cluster.center + (
                        direction / np.linalg.norm(direction)) * cluster.radius

                    cluster.instances.append(instance)


    def index_of_cluster_containing(self, instance: Any) -> Optional[int]:
        for i, cluster in enumerate(self.clusters):
            for _instance in cluster.instances:
                if np.array_equal(instance, _instance):
                    return i
        return None

    def describe(self) -> str:
        '''
        This describes this clustering algortihm's parameters 
        '''

        return f"ECM (distance_threshold: {self.distance_threshold})"

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
